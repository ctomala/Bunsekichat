import os
import secrets
from pathlib import Path

import pytest

from bunseki.academic.credential_capture import (
    CaptureReceipt,
    CredentialAwareEnrollmentOrchestrator,
    CredentialCapture,
    CredentialCaptureError,
)


pytestmark = pytest.mark.skipif(os.name != "nt", reason="requires Windows DPAPI")


def synthetic_credentials(count=1):
    return [
        {"username": f"synthetic-user-{index}", "temporary_password": secrets.token_urlsafe(24)}
        for index in range(count)
    ]


def capture(tmp_path):
    return CredentialCapture(destination=tmp_path / "private", repository_root=tmp_path / "repository")


def test_capture_is_encrypted_and_reveals_only_requested_credential(tmp_path, capsys):
    records = synthetic_credentials(2)
    vault = capture(tmp_path)
    receipt = vault.capture(records, manifest_sha256="a" * 64, execution_id="synthetic-run")
    raw = receipt.artifact_path.read_bytes()
    assert records[0]["temporary_password"].encode() not in raw
    assert records[0]["username"].encode() not in raw
    assert vault.reveal_one(receipt.artifact_path, records[1]["username"]) == records[1]["temporary_password"]
    with pytest.raises(CredentialCaptureError):
        vault.reveal_one(receipt.artifact_path, "missing")
    assert not capsys.readouterr().out
    vault.destroy(receipt.artifact_path)
    assert not receipt.artifact_path.exists()


def test_rejects_repository_destination_and_duplicate_identifiers(tmp_path):
    with pytest.raises(CredentialCaptureError):
        CredentialCapture(destination=tmp_path / "repository" / "nested", repository_root=tmp_path / "repository")
    vault = capture(tmp_path)
    duplicate = synthetic_credentials(1) * 2
    with pytest.raises(CredentialCaptureError):
        vault.capture(duplicate, manifest_sha256="b" * 64)


def test_corruption_fails_closed_and_capture_leaves_no_plaintext_temp_file(tmp_path):
    records = synthetic_credentials()
    vault = capture(tmp_path)
    receipt = vault.capture(records, manifest_sha256="c" * 64)
    receipt.artifact_path.write_bytes(b"not-an-artifact")
    with pytest.raises(CredentialCaptureError):
        vault.reveal_one(receipt.artifact_path, records[0]["username"])
    assert not list((tmp_path / "private").glob(".capture-*.tmp"))


class FakeConnection:
    autocommit = False

    def __init__(self, commit_fails=False, events=None):
        self.commits = 0
        self.rollbacks = 0
        self.commit_fails = commit_fails
        self.events = events

    def commit(self):
        self.commits += 1
        if self.events is not None:
            self.events.append("commit")
        if self.commit_fails:
            raise RuntimeError("synthetic commit failure")

    def rollback(self):
        self.rollbacks += 1
        if self.events is not None:
            self.events.append("rollback")


class FakeService:
    def __init__(self, connection, records, events=None, fails=False):
        self.connection = connection
        self.records = records
        self.called = False
        self.events = events
        self.fails = fails

    def bulk_enroll_for_teacher(self, teacher_user_id, context, rows):
        self.called = True
        if self.events is not None:
            self.events.append("service")
        if self.fails:
            raise RuntimeError("synthetic service failure")
        return self.records


def test_orchestrator_captures_before_commit(tmp_path):
    records = synthetic_credentials()
    service = FakeService(FakeConnection(), records)
    vault = capture(tmp_path)
    receipt = CredentialAwareEnrollmentOrchestrator(vault).enroll_and_capture(
        service, {}, [], teacher_user_id=1, manifest_sha256="d" * 64
    )
    assert service.called and service.connection.commits == 1 and service.connection.rollbacks == 0
    assert receipt.artifact_path.exists()
    vault.destroy(receipt.artifact_path)


def test_orchestrator_rolls_back_and_destroys_capture_when_commit_fails(tmp_path):
    records = synthetic_credentials()
    service = FakeService(FakeConnection(commit_fails=True), records)
    vault = capture(tmp_path)
    with pytest.raises(RuntimeError):
        CredentialAwareEnrollmentOrchestrator(vault).enroll_and_capture(
            service, {}, [], teacher_user_id=1, manifest_sha256="e" * 64
        )
    assert service.connection.rollbacks == 0
    artifacts = list((tmp_path / "private").glob("*.bunseki-credentials"))
    assert len(artifacts) == 1
    vault.destroy(artifacts[0])


def test_orchestrator_runs_nonsecret_validator_before_capture_and_commit(tmp_path):
    events = []
    records = [dict(item, user_id=index) for index, item in enumerate(synthetic_credentials(2), 1)]
    connection = FakeConnection(events=events)
    service = FakeService(connection, records, events=events)
    vault = capture(tmp_path)
    original_capture = vault.capture

    def tracked_capture(*args, **kwargs):
        events.append("capture")
        return original_capture(*args, **kwargs)

    vault.capture = tracked_capture

    def validator(state):
        events.append("validator")
        assert state.connection is connection
        assert state.context == {"synthetic": True}
        assert state.created_user_ids == (1, 2)
        assert state.credential_count == 2
        assert not hasattr(state, "temporary_password")

    receipt = CredentialAwareEnrollmentOrchestrator(vault).enroll_and_capture(
        service, {"synthetic": True}, [], teacher_user_id=1,
        manifest_sha256="f" * 64, pre_capture_validator=validator,
    )
    assert events == ["service", "validator", "capture", "commit"]
    vault.destroy(receipt.artifact_path)


def test_validator_failure_rolls_back_before_capture(tmp_path):
    records = synthetic_credentials()
    service = FakeService(FakeConnection(), records)
    vault = capture(tmp_path)

    with pytest.raises(RuntimeError):
        CredentialAwareEnrollmentOrchestrator(vault).enroll_and_capture(
            service, {}, [], teacher_user_id=1, manifest_sha256="g" * 64,
            pre_capture_validator=lambda state: (_ for _ in ()).throw(RuntimeError("synthetic validator failure")),
        )
    assert service.connection.rollbacks == 1 and service.connection.commits == 0
    assert not list((tmp_path / "private").glob("*.bunseki-credentials"))


def test_service_and_capture_failures_roll_back_without_artifact(tmp_path):
    failing_service = FakeService(FakeConnection(), [], fails=True)
    vault = capture(tmp_path)
    with pytest.raises(RuntimeError):
        CredentialAwareEnrollmentOrchestrator(vault).enroll_and_capture(
            failing_service, {}, [], teacher_user_id=1, manifest_sha256="h" * 64,
        )
    assert failing_service.connection.rollbacks == 1

    service = FakeService(FakeConnection(), synthetic_credentials())
    def fail_capture(*args, **kwargs):
        raise CredentialCaptureError("synthetic capture failure")
    vault.capture = fail_capture
    with pytest.raises(CredentialCaptureError):
        CredentialAwareEnrollmentOrchestrator(vault).enroll_and_capture(
            service, {}, [], teacher_user_id=1, manifest_sha256="i" * 64,
        )
    assert service.connection.rollbacks == 1 and not list((tmp_path / "private").glob("*.bunseki-credentials"))
