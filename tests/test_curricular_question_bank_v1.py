"""Focused unit tests for the additive curricular question-bank slice.

These tests intentionally load only the pure/question-bank functions from app.py so
they neither start Streamlit nor open a database connection.
"""
import ast
import json
import re
from datetime import datetime
from pathlib import Path
import unittest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
MIGRATION_PATH = Path(__file__).resolve().parents[1] / "migrations" / "019_curricular_question_bank_v1.sql"


def question_bank_namespace():
    tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
    names = {
        "now", "normalize_spaces", "get_plan_topic", "get_question_bank_items",
        "validate_question_bank_payload", "create_question_bank_drafts",
        "update_question_bank_item", "approve_question_bank_item",
        "reject_question_bank_item", "delete_question_bank_item",
        "generate_topic_question_drafts", "_strip_code_fences", "_safe_json_loads",
    }
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    ns = {"json": json, "re": re, "datetime": datetime}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(APP_PATH), "exec"), ns)
    ns["QUESTION_BANK_BLOOM_LEVELS"] = ("Recordar", "Comprender", "Aplicar", "Analizar", "Evaluar", "Crear")
    ns["QUESTION_BANK_DIFFICULTIES"] = ("Básico", "Intermedio", "Avanzado")
    return ns


def valid_payload():
    return {
        "question": "¿Cuál opción cumple el resultado?",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "Porque A aplica el procedimiento.",
        "bloom_level": "Aplicar",
        "difficulty_level": "Intermedio",
    }


def topic_context():
    return {
        "id": 7, "plan_id": 3, "unit_name": "Unidad 1", "topic": "Límites",
        "subtopic": "Laterales", "learning_outcome": "Calcula límites laterales",
        "bloom_level": "Aplicar", "keywords": "límites, laterales",
    }


class CurricularQuestionBankTests(unittest.TestCase):
    def test_migration_creates_constrained_traceable_table(self):
        sql = MIGRATION_PATH.read_text(encoding="utf-8")
        self.assertIn("CREATE TABLE IF NOT EXISTS question_bank_items", sql)
        self.assertIn("plan_topic_id INTEGER NOT NULL REFERENCES plan_topics(id)", sql)
        self.assertIn("learning_outcome TEXT", sql)
        self.assertIn("CHECK (status IN ('draft', 'approved', 'rejected', 'deleted'))", sql)

    def test_generated_question_is_saved_as_draft_with_curricular_traceability(self):
        qb, calls = question_bank_namespace(), []
        qb["get_plan_topic_for_actor"] = lambda plan_topic_id, actor_id: topic_context()
        qb["execute"] = lambda sql, params, returning=False: calls.append((sql, params)) or {"status": "draft", "plan_topic_id": params[1]}
        created = qb["create_question_bank_drafts"](11, 7, [valid_payload()], "gemini-test")
        self.assertEqual(created[0]["status"], "draft")
        self.assertEqual(calls[0][1][0:2], (3, 7))
        self.assertEqual(calls[0][1][10], "Calcula límites laterales")

    def test_drafts_rejected_and_deleted_are_not_requested_as_approved(self):
        qb, calls = question_bank_namespace(), []
        qb["fetchall"] = lambda sql, params: calls.append((sql, params)) or []
        qb["get_question_bank_items"](plan_topic_id=7, status="approved")
        self.assertIn("plan_topic_id=%s AND status=%s", calls[0][0])
        self.assertEqual(calls[0][1], (7, "approved"))
        source = APP_PATH.read_text(encoding="utf-8")
        self.assertIn("UPDATE question_bank_items SET status='deleted'", source)
        self.assertNotIn("DELETE FROM question_bank_items", source)

    def test_approve_changes_status_and_reject_delete_cannot_appear_in_approved_query(self):
        qb, calls = question_bank_namespace(), []
        qb["actor_can_manage_question_bank_item"] = lambda item_id, actor_id: True
        qb["execute"] = lambda sql, params, returning=False: calls.append((sql, params)) or {"status": "approved"}
        self.assertEqual(qb["approve_question_bank_item"](44, 11)["status"], "approved")
        self.assertIn("status='approved'", calls[0][0])
        self.assertIn("approved_by=%s", calls[0][0])
        self.assertIn("get_question_bank_items(plan_id=int(plan_id), status=\"approved\")", APP_PATH.read_text(encoding="utf-8"))

    def test_question_bank_mutations_require_authorized_actor(self):
        qb = question_bank_namespace()
        qb["actor_can_manage_question_bank_item"] = lambda item_id, actor_id: False
        with self.assertRaises(ValueError):
            qb["update_question_bank_item"](44, valid_payload(), 11)
        with self.assertRaises(ValueError):
            qb["approve_question_bank_item"](44, 11)
        with self.assertRaises(ValueError):
            qb["reject_question_bank_item"](44, 11)
        with self.assertRaises(ValueError):
            qb["delete_question_bank_item"](44, 11)

    def test_invalid_correct_answer_is_rejected(self):
        payload = valid_payload()
        payload["correct_answer"] = "No existe"
        with self.assertRaisesRegex(ValueError, "debe pertenecer"):
            question_bank_namespace()["validate_question_bank_payload"](payload)

    def test_teacher_generation_uses_one_topic_and_never_creates_adaptive_quiz(self):
        qb, prompts, payload = question_bank_namespace(), [], valid_payload()
        payload["topic"] = "Tema inventado por IA"
        qb["get_plan_topic_for_actor"] = lambda plan_topic_id, actor_id: topic_context()
        qb["ai_client"] = lambda: type("Client", (), {"models": type("Models", (), {"generate_content": lambda _, model, contents: prompts.append(contents) or type("Response", (), {"text": json.dumps([payload])})()})()})()
        qb["create_question_bank_drafts"] = lambda teacher_id, plan_topic_id, drafts, ai_model: drafts
        generated = qb["generate_topic_question_drafts"](11, 7, "Intermedio", 1)
        self.assertEqual(len(generated), 1)
        self.assertNotIn("topic", generated[0])
        self.assertIn("Tema obligatorio: Límites", prompts[0])
        self.assertIn("Calcula límites laterales", prompts[0])
        source = ast.get_source_segment(APP_PATH.read_text(encoding="utf-8"), next(n for n in ast.parse(APP_PATH.read_text(encoding="utf-8")).body if isinstance(n, ast.FunctionDef) and n.name == "generate_topic_question_drafts"))
        self.assertNotIn("create_adaptive_quiz", source)
        self.assertNotIn("adaptive_questions", source)
