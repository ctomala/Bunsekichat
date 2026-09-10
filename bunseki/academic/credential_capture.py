"""DPAPI-protected, local credential capture for approved enrollment runs.

This module intentionally does not connect to a database, generate passwords, or
deliver credentials.  It captures credentials that an enrollment service has
already generated, and it only accepts a caller-managed transaction for the
commit-after-capture workflow.
"""
from __future__ import annotations

import base64
import ctypes
import json
import os
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping


class CredentialCaptureError(RuntimeError):
    """Raised without including credential contents."""


class _DataBlob(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_uint32), ("pbData", ctypes.POINTER(ctypes.c_byte))]


class WindowsDpapi:
    """Minimal current-user DPAPI wrapper with no key material in the artifact."""

    CRYPTPROTECT_UI_FORBIDDEN = 0x1

    def __init__(self) -> None:
        if os.name != "nt":
            raise CredentialCaptureError("Windows DPAPI is unavailable on this platform")
        self._crypt32 = ctypes.windll.crypt32
        self._kernel32 = ctypes.windll.kernel32

    @staticmethod
    def _blob(data: bytes) -> tuple[_DataBlob, ctypes.Array[ctypes.c_char]]:
        buffer = ctypes.create_string_buffer(data)
        return _DataBlob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte))), buffer

    @staticmethod
    def _bytes(blob: _DataBlob) -> bytes:
        return ctypes.string_at(blob.pbData, blob.cbData)

    def protect(self, plaintext: bytes) -> bytes:
        source, source_buffer = self._blob(plaintext)
        result = _DataBlob()
        ok = self._crypt32.CryptProtectData(
            ctypes.byref(source), None, None, None, None,
            self.CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(result),
        )
        del source_buffer
        if not ok:
            raise CredentialCaptureError("DPAPI protection failed")
        try:
            return self._bytes(result)
        finally:
            self._kernel32.LocalFree(result.pbData)

    def unprotect(self, ciphertext: bytes) -> bytes:
        source, source_buffer = self._blob(ciphertext)
        result = _DataBlob()
        ok = self._crypt32.CryptUnprotectData(
            ctypes.byref(source), None, None, None, None,
            self.CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(result),
        )
        del source_buffer
        if not ok:
            raise CredentialCaptureError("DPAPI unprotection failed")
        try:
            return self._bytes(result)
        finally:
            self._kernel32.LocalFree(result.pbData)


@dataclass(frozen=True)
class CaptureReceipt:
    artifact_path: Path
    bundle_id: str
    credential_count: int


@dataclass(frozen=True)
class PreCaptureValidation:
    """Non-secret transaction-local data exposed to a pre-capture validator."""

    connection: object
    context: Mapping[str, object]
    created_user_ids: tuple[object, ...]
    credential_count: int


class CredentialCapture:
    """Captures encrypted bundles and only reveals one requested credential."""

    _MAGIC = b"BUNSEKI-DPAPI-1\n"

    def __init__(self, destination: Path | str | None = None, repository_root: Path | str | None = None) -> None:
        self.repository_root = Path(repository_root or Path(__file__).resolve().parents[2]).resolve()
        default = self.repository_root.parent / f"{self.repository_root.name}-private" / "credentials"
        self.destination = self._safe_destination(Path(destination or default))
        self._dpapi = WindowsDpapi()

    def _safe_destination(self, destination: Path) -> Path:
        resolved = destination.resolve()
        if resolved == self.repository_root or self.repository_root in resolved.parents:
            raise CredentialCaptureError("credential destination must be outside the repository")
        return resolved

    @staticmethod
    def _normalize(credentials: Iterable[Mapping[str, object]]) -> list[dict[str, str]]:
        normalized: list[dict[str, str]] = []
        identifiers: set[str] = set()
        for item in credentials:
            identifier = item.get("username", item.get("identifier"))
            password = item.get("temporary_password")
            if not isinstance(identifier, str) or not identifier or not isinstance(password, str) or not password:
                raise CredentialCaptureError("credential record is incomplete")
            if identifier in identifiers:
                raise CredentialCaptureError("duplicate credential identifier")
            identifiers.add(identifier)
            normalized.append({"identifier": identifier, "temporary_password": password})
        if not normalized:
            raise CredentialCaptureError("credential bundle is empty")
        return normalized

    def capture(
        self,
        credentials: Iterable[Mapping[str, object]],
        *,
        manifest_sha256: str,
        execution_id: str | None = None,
        destination: Path | str | None = None,
    ) -> CaptureReceipt:
        records = self._normalize(credentials)
        target = self._safe_destination(Path(destination)) if destination else self.destination
        bundle_id = execution_id or str(uuid.uuid4())
        payload = json.dumps(
            {
                "version": 1,
                "bundle_id": bundle_id,
                "manifest_sha256": manifest_sha256,
                "credentials": records,
            },
            separators=(",", ":"),
        ).encode("utf-8")
        encrypted = self._MAGIC + base64.b64encode(self._dpapi.protect(payload))
        target.mkdir(parents=True, exist_ok=True)
        artifact = target / f"{uuid.uuid4()}.bunseki-credentials"
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile("xb", dir=target, prefix=".capture-", suffix=".tmp", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(encrypted)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, artifact)
            return CaptureReceipt(artifact, bundle_id, len(records))
        except Exception as exc:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            if isinstance(exc, CredentialCaptureError):
                raise
            raise CredentialCaptureError("encrypted credential capture failed") from exc

    def _load(self, artifact: Path | str) -> dict[str, object]:
        raw = Path(artifact).read_bytes()
        if not raw.startswith(self._MAGIC):
            raise CredentialCaptureError("credential artifact format is invalid")
        try:
            payload = self._dpapi.unprotect(base64.b64decode(raw[len(self._MAGIC):], validate=True))
            parsed = json.loads(payload.decode("utf-8"))
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError, CredentialCaptureError) as exc:
            raise CredentialCaptureError("credential artifact cannot be opened safely") from exc
        if not isinstance(parsed, dict) or not isinstance(parsed.get("credentials"), list):
            raise CredentialCaptureError("credential artifact contents are invalid")
        return parsed

    def reveal_one(self, artifact: Path | str, identifier: str) -> str:
        if not isinstance(identifier, str) or not identifier:
            raise CredentialCaptureError("an explicit credential identifier is required")
        for item in self._load(artifact)["credentials"]:
            if isinstance(item, dict) and item.get("identifier") == identifier and isinstance(item.get("temporary_password"), str):
                return item["temporary_password"]
        raise CredentialCaptureError("credential identifier was not found")

    def destroy(self, artifact: Path | str) -> None:
        path = Path(artifact)
        if not path.is_file():
            raise CredentialCaptureError("credential artifact was not found")
        path.unlink()


class CredentialAwareEnrollmentOrchestrator:
    """Commits enrollment only after encrypted credential capture succeeds."""

    def __init__(self, capture: CredentialCapture) -> None:
        self.capture = capture

    def enroll_and_capture(self, service, context, rows, *, teacher_user_id, manifest_sha256: str, execution_id: str | None = None, pre_capture_validator: Callable[[PreCaptureValidation], None] | None = None) -> CaptureReceipt:
        connection = service.connection
        if connection.autocommit:
            raise CredentialCaptureError("caller-managed transaction is required before enrollment")
        receipt: CaptureReceipt | None = None
        commit_attempted = False
        try:
            credentials = service.bulk_enroll_for_teacher(teacher_user_id, context, rows)
            if pre_capture_validator is not None:
                pre_capture_validator(PreCaptureValidation(
                    connection=connection,
                    context=context,
                    created_user_ids=tuple(item.get("user_id") for item in credentials),
                    credential_count=len(credentials),
                ))
            receipt = self.capture.capture(credentials, manifest_sha256=manifest_sha256, execution_id=execution_id)
            commit_attempted = True
            connection.commit()
            return receipt
        except Exception:
            if not commit_attempted:
                connection.rollback()
                if receipt is not None:
                    self.capture.destroy(receipt.artifact_path)
            raise
