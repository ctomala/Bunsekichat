"""REQUIRES_DISPOSABLE_POSTGRES; fails closed without BUNSEKI_TEST_DATABASE_URL."""
import json
import os
import unittest
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
DSN = os.environ.get("BUNSEKI_TEST_DATABASE_URL")


@unittest.skipUnless(
    DSN and ("127.0.0.1" in DSN or "localhost" in DSN),
    "REQUIRES_DISPOSABLE_POSTGRES",
)
class TeacherAssessmentTargetingPostgresIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = psycopg2.connect(DSN)
        cls.db.autocommit = True
        with cls.db.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE users(
                    id SERIAL PRIMARY KEY,
                    username TEXT,
                    role TEXT,
                    active BOOLEAN NOT NULL DEFAULT TRUE
                );

                CREATE TABLE analytic_plans(
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    course TEXT,
                    subject TEXT,
                    course_level TEXT,
                    parallel TEXT,
                    shift TEXT,
                    teacher_id INTEGER REFERENCES users(id)
                );

                CREATE TABLE plan_topics(
                    id SERIAL PRIMARY KEY,
                    plan_id INTEGER REFERENCES analytic_plans(id) ON DELETE CASCADE,
                    unit_name TEXT,
                    topic TEXT,
                    subtopic TEXT,
                    learning_outcome TEXT,
                    bloom_level TEXT,
                    keywords TEXT
                );

                CREATE TABLE adaptive_quizzes(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    plan_id INTEGER REFERENCES analytic_plans(id),
                    title TEXT,
                    quiz_type TEXT,
                    source_topic TEXT,
                    difficulty TEXT,
                    subject TEXT,
                    course_level TEXT,
                    parallel TEXT,
                    shift TEXT,
                    cohort TEXT,
                    question_count INTEGER,
                    status TEXT,
                    score DOUBLE PRECISION,
                    passed BOOLEAN,
                    created_at TEXT,
                    completed_at TEXT
                );

                CREATE TABLE adaptive_questions(
                    id SERIAL PRIMARY KEY,
                    quiz_id INTEGER REFERENCES adaptive_quizzes(id),
                    question TEXT,
                    options_json TEXT,
                    correct_answer TEXT,
                    position INTEGER,
                    topic TEXT,
                    subtopic TEXT,
                    difficulty_level TEXT,
                    explanation TEXT,
                    bloom_level TEXT,
                    user_answer TEXT,
                    is_correct BOOLEAN,
                    response_time_seconds DOUBLE PRECISION
                );
                """
            )

            for name in (
                "019_curricular_question_bank_v1.sql",
                "020_curricular_assessment_traceability_v2.sql",
                "021_teacher_assessment_targeting_v3.sql",
            ):
                cur.execute((ROOT / "migrations" / name).read_text(encoding="utf-8"))

            cur.execute(
                """
                CREATE TABLE profiles(
                    user_id INTEGER PRIMARY KEY,
                    research_group TEXT
                );
                ALTER TABLE adaptive_quizzes ADD COLUMN version_code TEXT;
                ALTER TABLE adaptive_questions ADD COLUMN item_code TEXT;
                ALTER TABLE adaptive_questions ADD COLUMN dimension TEXT;
                ALTER TABLE adaptive_questions ADD COLUMN conceptual_error TEXT;
                """
            )

        import app

        # The production connector defaults to sslmode=require. The disposable
        # localhost container intentionally has no SSL, so force SSL off only
        # for this isolated test process.
        app.DATABASE_URL = (
            DSN
            if "sslmode=" in DSN.lower()
            else DSN + ("&" if "?" in DSN else "?") + "sslmode=disable"
        )
        cls.app = app

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def _create_plan_and_item(self, suffix):
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users(username,role,active)
                VALUES(%s,'teacher',TRUE)
                RETURNING id
                """,
                (f"teacher_{suffix}",),
            )
            teacher_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO analytic_plans(
                    title,course,subject,course_level,parallel,shift,teacher_id
                )
                VALUES(
                    %s,
                    '4-4-A1 Matutino',
                    'Cálculo Diferencial',
                    '4',
                    '4-A1',
                    'Matutino',
                    %s
                )
                RETURNING id
                """,
                (f"Plan {suffix}", teacher_id),
            )
            plan_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO plan_topics(
                    plan_id,unit_name,topic,subtopic,learning_outcome,bloom_level,keywords
                )
                VALUES(
                    %s,
                    'Unidad 1',
                    'Optimización mediante derivadas',
                    'Máximos y mínimos',
                    'Resolver problemas de optimización aplicando derivadas.',
                    'Aplicar',
                    'derivada,optimización'
                )
                RETURNING id
                """,
                (plan_id,),
            )
            topic_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO question_bank_items(
                    plan_id,plan_topic_id,created_by,approved_by,
                    question,options_json,correct_answer,explanation,
                    unit_name,topic,subtopic,learning_outcome,
                    bloom_level,difficulty_level,status,source,
                    created_at,approved_at
                )
                VALUES(
                    %s,%s,%s,%s,
                    %s,
                    %s,
                    'A',
                    'Explicación piloto',
                    'Unidad 1',
                    'Optimización mediante derivadas',
                    'Máximos y mínimos',
                    'Resolver problemas de optimización aplicando derivadas.',
                    'Aplicar',
                    'Intermedio',
                    'approved',
                    'test',
                    '2026-09-12T00:00:00',
                    '2026-09-12T00:00:00'
                )
                RETURNING id
                """,
                (
                    plan_id,
                    topic_id,
                    teacher_id,
                    teacher_id,
                    f"Pregunta {suffix}",
                    json.dumps(["A", "B", "C", "D"]),
                ),
            )
            item_id = cur.fetchone()[0]

        return teacher_id, plan_id, item_id

    @staticmethod
    def _context():
        return {
            "subject": "Cálculo Diferencial",
            "course_level": "4",
            "parallel": "4-A1",
            "shift": "Matutino",
            "cohort": "4-4-A1 Matutino",
        }

    def test_publish_targeted_without_targets_fails_closed(self):
        a = self.app
        teacher_id, plan_id, item_id = self._create_plan_and_item("no_targets")
        ctx = self._context()

        assessment = a.create_teacher_assessment(
            teacher_id,
            plan_id,
            "Target sin destinatarios",
            ctx,
        )
        a.set_teacher_assessment_items(
            assessment["id"],
            teacher_id,
            [item_id],
        )

        with self.db.cursor() as cur:
            cur.execute(
                """
                UPDATE teacher_assessments
                SET audience_mode='targeted'
                WHERE id=%s
                """,
                (assessment["id"],),
            )

        with self.assertRaises(ValueError):
            a.publish_teacher_assessment(
                assessment["id"],
                teacher_id,
            )

    def test_targeted_flow_denies_unassigned_student_and_keeps_context_guard(self):
        a = self.app
        teacher_id, plan_id, item_id = self._create_plan_and_item("flow")
        ctx = self._context()

        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users(username,role,active)
                VALUES
                    ('student_target','student',TRUE),
                    ('student_other','student',TRUE),
                    ('student_inactive','student',FALSE)
                RETURNING id
                """
            )
            student_target, student_other, student_inactive = [
                row[0] for row in cur.fetchall()
            ]

        assessment = a.create_teacher_assessment(
            teacher_id,
            plan_id,
            "Evaluación targeted",
            ctx,
        )
        a.set_teacher_assessment_items(
            assessment["id"],
            teacher_id,
            [item_id],
        )

        with self.assertRaises(ValueError):
            a.set_teacher_assessment_audience(
                assessment["id"],
                teacher_id,
                "targeted",
                [],
            )

        with self.assertRaises(ValueError):
            a.set_teacher_assessment_audience(
                assessment["id"],
                teacher_id,
                "targeted",
                [student_inactive],
            )

        a.set_teacher_assessment_audience(
            assessment["id"],
            teacher_id,
            "targeted",
            [student_target],
        )

        self.assertEqual(
            a.get_teacher_assessment_target_user_ids(assessment["id"]),
            [student_target],
        )

        a.publish_teacher_assessment(
            assessment["id"],
            teacher_id,
        )

        self.assertEqual(
            [
                row["id"]
                for row in a.get_student_teacher_assessments(
                    ctx,
                    student_target,
                )
            ],
            [assessment["id"]],
        )
        self.assertEqual(
            a.get_student_teacher_assessments(
                ctx,
                student_other,
            ),
            [],
        )
        self.assertEqual(
            a.get_student_teacher_assessments(
                {**ctx, "parallel": "4-B1"},
                student_target,
            ),
            [],
        )

        quiz = a.start_teacher_assessment_attempt(
            student_target,
            assessment["id"],
            ctx,
        )
        self.assertEqual(
            quiz["user_id"],
            student_target,
        )

        with self.assertRaises(ValueError):
            a.start_teacher_assessment_attempt(
                student_other,
                assessment["id"],
                ctx,
            )

        with self.assertRaises(ValueError):
            a.start_teacher_assessment_attempt(
                student_target,
                assessment["id"],
                {**ctx, "parallel": "4-B1"},
            )


if __name__ == "__main__":
    unittest.main()
