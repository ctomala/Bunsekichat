"""REQUIRES_DISPOSABLE_POSTGRES: never reads DATABASE_URL or .env."""
import os
from pathlib import Path
import unittest
import psycopg2

DSN = os.environ.get("BUNSEKI_TEST_DATABASE_URL")
pytestmark = None

@unittest.skipUnless(DSN and ("127.0.0.1" in DSN or "localhost" in DSN), "REQUIRES_DISPOSABLE_POSTGRES loopback BUNSEKI_TEST_DATABASE_URL")
class CurricularPostgresIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = psycopg2.connect(DSN); cls.db.autocommit = True
        with cls.db.cursor() as cur:
            cur.execute("""CREATE TABLE users(id SERIAL PRIMARY KEY,username TEXT); CREATE TABLE analytic_plans(id SERIAL PRIMARY KEY,title TEXT,course TEXT,subject TEXT,course_level TEXT,parallel TEXT,shift TEXT); CREATE TABLE plan_topics(id SERIAL PRIMARY KEY,plan_id INTEGER REFERENCES analytic_plans(id) ON DELETE CASCADE,unit_name TEXT,topic TEXT,subtopic TEXT,learning_outcome TEXT,bloom_level TEXT,keywords TEXT); CREATE TABLE adaptive_quizzes(id SERIAL PRIMARY KEY,user_id INTEGER REFERENCES users(id),plan_id INTEGER REFERENCES analytic_plans(id),title TEXT,quiz_type TEXT,source_topic TEXT,difficulty TEXT,subject TEXT,course_level TEXT,parallel TEXT,shift TEXT,cohort TEXT,question_count INTEGER,status TEXT,score DOUBLE PRECISION,passed BOOLEAN,created_at TEXT,completed_at TEXT); CREATE TABLE adaptive_questions(id SERIAL PRIMARY KEY,quiz_id INTEGER REFERENCES adaptive_quizzes(id) ON DELETE CASCADE,question TEXT,options_json TEXT,correct_answer TEXT,position INTEGER,topic TEXT,subtopic TEXT,difficulty_level TEXT,explanation TEXT,bloom_level TEXT,user_answer TEXT,is_correct BOOLEAN,response_time_seconds DOUBLE PRECISION);""")
            for name in ("019_curricular_question_bank_v1.sql", "020_curricular_assessment_traceability_v2.sql"):
                cur.execute((Path(__file__).resolve().parents[1] / "migrations" / name).read_text(encoding="utf-8"))
    @classmethod
    def tearDownClass(cls): cls.db.close()
    def test_real_postgres_migrations_and_core_constraints(self):
        with self.db.cursor() as cur:
            cur.execute("INSERT INTO users(username) VALUES('teacher'),('student1'),('student2') RETURNING id"); users=[r[0] for r in cur.fetchall()]
            cur.execute("INSERT INTO analytic_plans(title,subject,course_level,parallel,shift) VALUES('P','Math','1','A','AM') RETURNING id"); plan=cur.fetchone()[0]
            cur.execute("INSERT INTO plan_topics(plan_id,topic,learning_outcome) VALUES(%s,'Topic','Outcome') RETURNING id",(plan,)); topic=cur.fetchone()[0]
            cur.execute("INSERT INTO question_bank_items(plan_id,plan_topic_id,created_by,question,options_json,correct_answer,topic,learning_outcome,status,source,created_at) VALUES(%s,%s,%s,'Q','[\"A\",\"B\",\"C\",\"D\"]','A','Topic','Outcome','approved','ai','now') RETURNING id",(plan,topic,users[0])); bank=cur.fetchone()[0]
            cur.execute("INSERT INTO teacher_assessments(created_by,plan_id,title,status,created_at) VALUES(%s,%s,'A','published','now') RETURNING id",(users[0],plan)); assessment=cur.fetchone()[0]
            cur.execute("INSERT INTO teacher_assessment_items(assessment_id,question_bank_item_id,position) VALUES(%s,%s,1)",(assessment,bank))
            cur.execute("INSERT INTO adaptive_quizzes(user_id,plan_id,quiz_type,teacher_assessment_id,status,created_at) VALUES(%s,%s,'bank_assessment',%s,'generated','now') RETURNING id",(users[1],plan,assessment)); quiz=cur.fetchone()[0]
            cur.execute("INSERT INTO adaptive_questions(quiz_id,question,options_json,correct_answer,position,topic,question_bank_item_id,plan_topic_id,learning_outcome) VALUES(%s,'Q','[\"A\",\"B\",\"C\",\"D\"]','A',1,'Topic',%s,%s,'Outcome')",(quiz,bank,topic))
            with self.assertRaises(Exception): cur.execute("INSERT INTO adaptive_quizzes(user_id,teacher_assessment_id,status,created_at) VALUES(%s,%s,'generated','now')",(users[1],assessment))
            with self.assertRaises(Exception): cur.execute("INSERT INTO question_bank_items(plan_id,plan_topic_id,question,options_json,correct_answer,topic,status,source,created_at) VALUES(%s,%s,'x','[]','x','x','bad','ai','now')",(plan,topic))
            cur.execute("SELECT question_bank_item_id,plan_topic_id,learning_outcome FROM adaptive_questions WHERE quiz_id=%s",(quiz,)); self.assertEqual(cur.fetchone(),(bank,topic,'Outcome'))
