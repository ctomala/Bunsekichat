"""
BunsekiChat
P5A6C1 - Resumable Assessment Attempt Service

Database-backed source of truth for assessment progress.

This module deliberately contains no Streamlit dependencies.

Transaction policy:
    Functions DO NOT commit or close the supplied connection.
    The caller owns COMMIT / ROLLBACK / CLOSE.

This allows:
    - atomic application workflows,
    - deterministic automated tests,
    - rollback-safe production certification.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from psycopg2.extras import Json, RealDictCursor


VALID_ASSESSMENT_KINDS = {
    "pretest",
    "posttest",
    "adaptive",
    "teacher_assessment",
    "research",
    "practice",
    "other",
}


class AttemptError(RuntimeError):
    """Base error for the resumable assessment engine."""


class AttemptNotFoundError(AttemptError):
    """Attempt does not exist or is not accessible by this user."""


class AttemptStateError(AttemptError):
    """Operation is not valid for the current attempt state."""


def _require_positive_id(value: Any, name: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc

    if parsed <= 0:
        raise ValueError(f"{name} must be > 0")

    return parsed


def _nonnegative_int(value: Any, name: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc

    if parsed < 0:
        raise ValueError(f"{name} must be >= 0")

    return parsed


def _clean_source_key(source_key: str) -> str:
    key = str(source_key or "").strip()

    if not key:
        raise ValueError("source_key is required")

    return key


def _validate_kind(assessment_kind: str) -> str:
    kind = str(assessment_kind or "").strip()

    if kind not in VALID_ASSESSMENT_KINDS:
        raise ValueError(
            f"Unsupported assessment_kind: {kind}"
        )

    return kind


def _row_to_dict(row) -> Optional[Dict[str, Any]]:
    if row is None:
        return None

    return dict(row)


def get_active_attempt(
    connection,
    *,
    user_id: int,
    assessment_kind: str,
    source_key: str,
) -> Optional[Dict[str, Any]]:
    """
    Return the current active attempt for one user/instrument.
    """

    user_id = _require_positive_id(
        user_id,
        "user_id",
    )

    assessment_kind = _validate_kind(
        assessment_kind
    )

    source_key = _clean_source_key(
        source_key
    )

    with connection.cursor(
        cursor_factory=RealDictCursor
    ) as cur:

        cur.execute(
            """
            SELECT *
            FROM public.assessment_attempts
            WHERE user_id = %s
              AND assessment_kind = %s
              AND source_key = %s
              AND status = 'in_progress'
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                user_id,
                assessment_kind,
                source_key,
            ),
        )

        return _row_to_dict(
            cur.fetchone()
        )


def get_or_create_attempt(
    connection,
    *,
    user_id: int,
    assessment_kind: str,
    source_key: str,
    adaptive_quiz_id: Optional[int] = None,
    teacher_assessment_id: Optional[int] = None,
    research_test_id: Optional[int] = None,
    version_code: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Return the active attempt or create it.

    Safe against duplicate active attempts because PostgreSQL
    provides the final uniqueness guarantee.
    """

    user_id = _require_positive_id(
        user_id,
        "user_id",
    )

    assessment_kind = _validate_kind(
        assessment_kind
    )

    source_key = _clean_source_key(
        source_key
    )

    if adaptive_quiz_id is not None:
        adaptive_quiz_id = _require_positive_id(
            adaptive_quiz_id,
            "adaptive_quiz_id",
        )

    if teacher_assessment_id is not None:
        teacher_assessment_id = _require_positive_id(
            teacher_assessment_id,
            "teacher_assessment_id",
        )

    if research_test_id is not None:
        research_test_id = _require_positive_id(
            research_test_id,
            "research_test_id",
        )

    existing = get_active_attempt(
        connection,
        user_id=user_id,
        assessment_kind=assessment_kind,
        source_key=source_key,
    )

    if existing is not None:
        existing["created"] = False
        return existing

    with connection.cursor(
        cursor_factory=RealDictCursor
    ) as cur:

        cur.execute(
            """
            INSERT INTO public.assessment_attempts (
                user_id,
                assessment_kind,
                source_key,
                adaptive_quiz_id,
                teacher_assessment_id,
                research_test_id,
                version_code,
                metadata_json
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            ON CONFLICT DO NOTHING
            RETURNING *
            """,
            (
                user_id,
                assessment_kind,
                source_key,
                adaptive_quiz_id,
                teacher_assessment_id,
                research_test_id,
                (
                    str(version_code).strip()
                    if version_code is not None
                    else None
                ),
                Json(metadata or {}),
            ),
        )

        inserted = cur.fetchone()

        if inserted is not None:
            result = dict(inserted)
            result["created"] = True
            return result

    # A concurrent request may have created the same active
    # instrument between SELECT and INSERT.
    existing = get_active_attempt(
        connection,
        user_id=user_id,
        assessment_kind=assessment_kind,
        source_key=source_key,
    )

    if existing is not None:
        existing["created"] = False
        return existing

    # Another partial unique constraint may have blocked the
    # insert, most notably one active attempt for adaptive quiz.
    if adaptive_quiz_id is not None:

        with connection.cursor(
            cursor_factory=RealDictCursor
        ) as cur:

            cur.execute(
                """
                SELECT *
                FROM public.assessment_attempts
                WHERE user_id = %s
                  AND adaptive_quiz_id = %s
                  AND status = 'in_progress'
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    user_id,
                    adaptive_quiz_id,
                ),
            )

            conflicting = cur.fetchone()

            if conflicting is not None:
                raise AttemptStateError(
                    "An active attempt already exists for "
                    "this adaptive quiz under another source key."
                )

    raise AttemptStateError(
        "Could not create or recover the active attempt."
    )


def load_attempt_progress(
    connection,
    *,
    attempt_id: int,
    user_id: int,
) -> Dict[str, Any]:
    """
    Load one attempt plus all autosaved responses.

    Ownership is enforced by user_id.
    """

    attempt_id = _require_positive_id(
        attempt_id,
        "attempt_id",
    )

    user_id = _require_positive_id(
        user_id,
        "user_id",
    )

    with connection.cursor(
        cursor_factory=RealDictCursor
    ) as cur:

        cur.execute(
            """
            SELECT *
            FROM public.assessment_attempts
            WHERE id = %s
              AND user_id = %s
            """,
            (
                attempt_id,
                user_id,
            ),
        )

        attempt = cur.fetchone()

        if attempt is None:
            raise AttemptNotFoundError(
                "Attempt not found for this user."
            )

        cur.execute(
            """
            SELECT
                id,
                attempt_id,
                question_key,
                question_id,
                answer_json,
                first_answered_at,
                updated_at,
                elapsed_seconds,
                change_count
            FROM public.assessment_attempt_answers
            WHERE attempt_id = %s
            ORDER BY id
            """,
            (
                attempt_id,
            ),
        )

        answer_rows = [
            dict(row)
            for row in cur.fetchall()
        ]

    answers_by_key = {
        row["question_key"]: row
        for row in answer_rows
    }

    return {
        "attempt": dict(attempt),
        "answers": answer_rows,
        "answers_by_key": answers_by_key,
        "answered_count": len(answer_rows),
    }


def save_attempt_answer(
    connection,
    *,
    attempt_id: int,
    user_id: int,
    question_key: str,
    answer_payload: Any,
    question_id: Optional[int] = None,
    elapsed_seconds: int = 0,
    current_position: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Persist one response immediately.

    Re-saving the same question performs an UPSERT.

    change_count increases only when the JSON answer changes.
    """

    attempt_id = _require_positive_id(
        attempt_id,
        "attempt_id",
    )

    user_id = _require_positive_id(
        user_id,
        "user_id",
    )

    question_key = str(
        question_key or ""
    ).strip()

    if not question_key:
        raise ValueError(
            "question_key is required"
        )

    if question_id is not None:
        question_id = _require_positive_id(
            question_id,
            "question_id",
        )

    elapsed_seconds = _nonnegative_int(
        elapsed_seconds,
        "elapsed_seconds",
    )

    if current_position is not None:
        current_position = _nonnegative_int(
            current_position,
            "current_position",
        )

    with connection.cursor(
        cursor_factory=RealDictCursor
    ) as cur:

        # Lock the parent attempt so submit/autosave cannot race.
        cur.execute(
            """
            SELECT id, status
            FROM public.assessment_attempts
            WHERE id = %s
              AND user_id = %s
            FOR UPDATE
            """,
            (
                attempt_id,
                user_id,
            ),
        )

        attempt = cur.fetchone()

        if attempt is None:
            raise AttemptNotFoundError(
                "Attempt not found for this user."
            )

        if attempt["status"] != "in_progress":
            raise AttemptStateError(
                "Answers can only be saved while "
                "the attempt is in progress."
            )

        cur.execute(
            """
            INSERT INTO public.assessment_attempt_answers (
                attempt_id,
                question_key,
                question_id,
                answer_json,
                first_answered_at,
                updated_at,
                elapsed_seconds,
                change_count
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                %s,
                0
            )
            ON CONFLICT (
                attempt_id,
                question_key
            )
            DO UPDATE SET
                question_id = COALESCE(
                    EXCLUDED.question_id,
                    public.assessment_attempt_answers.question_id
                ),
                answer_json = EXCLUDED.answer_json,
                first_answered_at = COALESCE(
                    public.assessment_attempt_answers.first_answered_at,
                    EXCLUDED.first_answered_at
                ),
                updated_at = CURRENT_TIMESTAMP,
                elapsed_seconds = GREATEST(
                    public.assessment_attempt_answers.elapsed_seconds,
                    EXCLUDED.elapsed_seconds
                ),
                change_count =
                    public.assessment_attempt_answers.change_count
                    +
                    CASE
                        WHEN
                            public.assessment_attempt_answers.answer_json
                            IS DISTINCT FROM
                            EXCLUDED.answer_json
                        THEN 1
                        ELSE 0
                    END
            RETURNING *
            """,
            (
                attempt_id,
                question_key,
                question_id,
                Json(answer_payload),
                elapsed_seconds,
            ),
        )

        answer = dict(
            cur.fetchone()
        )

        cur.execute(
            """
            UPDATE public.assessment_attempts
            SET
                last_activity_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP,
                elapsed_seconds = GREATEST(
                    elapsed_seconds,
                    %s
                ),
                current_position =
                    CASE
                        WHEN %s IS NULL
                        THEN current_position
                        ELSE %s
                    END
            WHERE id = %s
              AND user_id = %s
              AND status = 'in_progress'
            RETURNING *
            """,
            (
                elapsed_seconds,
                current_position,
                current_position,
                attempt_id,
                user_id,
            ),
        )

        updated_attempt = cur.fetchone()

        if updated_attempt is None:
            raise AttemptStateError(
                "Attempt changed state during autosave."
            )

    return {
        "attempt": dict(updated_attempt),
        "answer": answer,
    }


def resume_attempt(
    connection,
    *,
    attempt_id: int,
    user_id: int,
) -> Dict[str, Any]:
    """
    Register an explicit recovery/re-entry event.
    """

    attempt_id = _require_positive_id(
        attempt_id,
        "attempt_id",
    )

    user_id = _require_positive_id(
        user_id,
        "user_id",
    )

    with connection.cursor(
        cursor_factory=RealDictCursor
    ) as cur:

        cur.execute(
            """
            UPDATE public.assessment_attempts
            SET
                resume_count = resume_count + 1,
                last_activity_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND user_id = %s
              AND status = 'in_progress'
            RETURNING *
            """,
            (
                attempt_id,
                user_id,
            ),
        )

        row = cur.fetchone()

        if row is not None:
            return dict(row)

        cur.execute(
            """
            SELECT status
            FROM public.assessment_attempts
            WHERE id = %s
              AND user_id = %s
            """,
            (
                attempt_id,
                user_id,
            ),
        )

        existing = cur.fetchone()

        if existing is None:
            raise AttemptNotFoundError(
                "Attempt not found for this user."
            )

        raise AttemptStateError(
            f"Attempt cannot be resumed from "
            f"status={existing['status']}."
        )


def submit_attempt(
    connection,
    *,
    attempt_id: int,
    user_id: int,
    elapsed_seconds: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Finalize an attempt exactly once.

    Repeating submit on an already submitted attempt is safe:
    submitted_at is preserved and no second finalization occurs.
    """

    attempt_id = _require_positive_id(
        attempt_id,
        "attempt_id",
    )

    user_id = _require_positive_id(
        user_id,
        "user_id",
    )

    if elapsed_seconds is not None:
        elapsed_seconds = _nonnegative_int(
            elapsed_seconds,
            "elapsed_seconds",
        )

    with connection.cursor(
        cursor_factory=RealDictCursor
    ) as cur:

        cur.execute(
            """
            SELECT *
            FROM public.assessment_attempts
            WHERE id = %s
              AND user_id = %s
            FOR UPDATE
            """,
            (
                attempt_id,
                user_id,
            ),
        )

        attempt = cur.fetchone()

        if attempt is None:
            raise AttemptNotFoundError(
                "Attempt not found for this user."
            )

        if attempt["status"] == "submitted":
            result = dict(attempt)
            result["already_submitted"] = True
            return result

        if attempt["status"] != "in_progress":
            raise AttemptStateError(
                f"Attempt cannot be submitted from "
                f"status={attempt['status']}."
            )

        cur.execute(
            """
            UPDATE public.assessment_attempts
            SET
                status = 'submitted',
                submitted_at = COALESCE(
                    submitted_at,
                    CURRENT_TIMESTAMP
                ),
                last_activity_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP,
                elapsed_seconds =
                    CASE
                        WHEN %s IS NULL
                        THEN elapsed_seconds
                        ELSE GREATEST(
                            elapsed_seconds,
                            %s
                        )
                    END
            WHERE id = %s
              AND user_id = %s
              AND status = 'in_progress'
            RETURNING *
            """,
            (
                elapsed_seconds,
                elapsed_seconds,
                attempt_id,
                user_id,
            ),
        )

        submitted = cur.fetchone()

        if submitted is None:
            raise AttemptStateError(
                "Attempt changed state during submission."
            )

        result = dict(submitted)
        result["already_submitted"] = False

        return result
