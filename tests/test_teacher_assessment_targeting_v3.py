"""Contract tests for teacher-assessment targeting V3."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "app.py").read_text(encoding="utf-8")
SQL = (ROOT / "migrations" / "021_teacher_assessment_targeting_v3.sql").read_text(encoding="utf-8")


def function_source(name):
    node = next(node for node in ast.parse(APP).body if isinstance(node, ast.FunctionDef) and node.name == name)
    return ast.get_source_segment(APP, node)


class TeacherAssessmentTargetingV3Tests(unittest.TestCase):
    def test_schema_adds_audience_mode_and_target_table(self):
        self.assertIn("audience_mode", SQL)
        self.assertIn("'academic_context','targeted'", SQL)
        self.assertIn("CREATE TABLE IF NOT EXISTS teacher_assessment_targets", SQL)
        self.assertIn("PRIMARY KEY (assessment_id, user_id)", SQL)

    def test_target_configuration_is_draft_creator_only_and_validates_students(self):
        source = function_source("set_teacher_assessment_audience")
        self.assertIn('assessment["status"] != "draft"', source)
        self.assertIn('assessment["created_by"] != teacher_id', source)
        self.assertIn("role='student'", source)
        self.assertIn("active=TRUE", source)
        self.assertIn("necesita al menos un estudiante", source)

    def test_target_configuration_enforces_teacher_scope_and_context(self):
        source = function_source("set_teacher_assessment_audience")
        self.assertIn("get_teacher_assessment_eligible_students", source)
        self.assertIn("alcance del ", source)
        self.assertIn("docente y coincidir", source)
        helper = function_source("get_teacher_assessment_eligible_students")
        self.assertIn("teacher_parallels", helper)
        self.assertIn("enrollments", helper)
        self.assertIn("assessment_matches_academic_context", helper)
        self.assertIn("u.active=TRUE", helper)

    def test_teacher_plan_ui_exposes_audience_editor(self):
        source = function_source("render_teacher_plan_manager")
        self.assertIn("Modo de audiencia", source)
        self.assertIn("Estudiantes destinatarios", source)
        self.assertIn("set_teacher_assessment_audience", source)
        self.assertIn("get_teacher_assessment_target_user_ids", source)

    def test_academic_context_mode_rejects_individual_targets(self):
        source = function_source("set_teacher_assessment_audience")
        self.assertIn('mode == "academic_context" and ids', source)
        self.assertIn("no admite destinatarios individuales", source)

    def test_targeted_access_is_deny_by_default_and_keeps_context_guard(self):
        source = function_source("assessment_allows_student")
        self.assertIn('mode != "targeted" or not user_id', source)
        self.assertIn("assessment_matches_academic_context", source)
        self.assertIn("teacher_assessment_targets", source)

    def test_student_listing_passes_user_id_through_authorization(self):
        source = function_source("get_student_teacher_assessments")
        self.assertIn("user_id=None", source)
        self.assertIn("assessment_allows_student(row, user_id, academic_context)", source)

    def test_publish_blocks_targeted_assessment_without_targets(self):
        source = function_source("publish_teacher_assessment")
        self.assertIn('mode == "targeted"', source)
        self.assertIn("get_teacher_assessment_target_user_ids", source)
        self.assertIn("sin estudiantes destinatarios", source)

    def test_publish_revalidates_target_scope_and_context(self):
        source = function_source("publish_teacher_assessment")
        self.assertIn("get_teacher_assessment_eligible_students", source)
        self.assertIn("issubset", source)
        self.assertIn("fuera del alcance docente", source)

    def test_attempt_start_uses_same_target_authorization_gate(self):
        source = function_source("start_teacher_assessment_attempt")
        self.assertIn("assessment_allows_student(assessment, user_id, academic_context)", source)
        self.assertIn("no está asignada a este estudiante", source)
        self.assertIn("if existing:", source)


if __name__ == "__main__":
    unittest.main()
