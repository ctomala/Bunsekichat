"""Contract tests for the additive teacher-assessment traceability slice.

They inspect the isolated V2 functions without importing Streamlit or opening a DB.
"""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "app.py").read_text(encoding="utf-8")
SQL = (ROOT / "migrations" / "020_curricular_assessment_traceability_v2.sql").read_text(encoding="utf-8")


def function_source(name):
    node = next(node for node in ast.parse(APP).body if isinstance(node, ast.FunctionDef) and node.name == name)
    return ast.get_source_segment(APP, node)


class CurricularAssessmentTraceabilityTests(unittest.TestCase):
    def test_schema_has_assessments_items_and_single_attempt_guard(self):
        self.assertIn("CREATE TABLE IF NOT EXISTS teacher_assessments", SQL)
        self.assertIn("CREATE TABLE IF NOT EXISTS teacher_assessment_items", SQL)
        self.assertIn("uq_adaptive_quizzes_teacher_assessment_student", SQL)

    def test_assessments_start_draft_and_items_require_approved(self):
        self.assertIn("'draft'", function_source("create_teacher_assessment"))
        self.assertIn("status='approved'", function_source("set_teacher_assessment_items"))

    def test_only_drafts_can_change_items_and_publish_requires_items(self):
        source = function_source("set_teacher_assessment_items")
        self.assertIn('assessment["status"] != "draft"', source)
        self.assertIn("sin preguntas", function_source("publish_teacher_assessment"))

    def test_publish_close_and_context_matching_are_explicit(self):
        self.assertIn("status='published'", function_source("publish_teacher_assessment"))
        self.assertIn("status='closed'", function_source("close_teacher_assessment"))
        self.assertIn("subject", function_source("assessment_matches_academic_context"))
        self.assertIn("parallel", function_source("assessment_matches_academic_context"))

    def test_start_uses_bank_assessment_snapshot_without_ai(self):
        source = function_source("start_teacher_assessment_attempt")
        self.assertIn("'bank_assessment'", source)
        self.assertIn("question_bank_item_id", source)
        self.assertIn("plan_topic_id", source)
        self.assertIn("learning_outcome", source)
        self.assertNotIn("generate_questions_with_ai", source)
        self.assertNotIn("ai_client", source)

    def test_start_blocks_closed_or_wrong_context_and_reuses_existing_attempt(self):
        source = function_source("start_teacher_assessment_attempt")
        self.assertIn('assessment["status"] != "published"', source)
        self.assertIn("assessment_matches_academic_context", source)
        self.assertIn("if existing: return existing", source)

    def test_grading_records_answers_and_score_without_ai(self):
        source = function_source("grade_teacher_assessment_attempt")
        self.assertIn("user_answer=%s,is_correct=%s", source)
        self.assertIn("score=%s,passed=%s,status='completed'", source)
        self.assertNotIn("generate_questions_with_ai", source)

    def test_curricular_analytics_has_all_required_dimensions(self):
        source = function_source("get_teacher_assessment_curricular_analytics")
        for dimension in ("topic", "learning_outcome", "bloom_level", "difficulty_level"):
            self.assertIn(dimension, source)

    def test_student_ui_is_separate_and_only_uses_published_matching_assessments(self):
        self.assertIn("### Evaluaciones del docente", APP)
        self.assertIn('get_student_teacher_assessments(academic_context, user["id"])', APP)
