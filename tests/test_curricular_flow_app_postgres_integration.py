"""REQUIRES_DISPOSABLE_POSTGRES; fails closed without BUNSEKI_TEST_DATABASE_URL."""
import json, os, unittest
from pathlib import Path
import psycopg2

DSN=os.environ.get("BUNSEKI_TEST_DATABASE_URL")
@unittest.skipUnless(DSN and ("127.0.0.1" in DSN or "localhost" in DSN),"REQUIRES_DISPOSABLE_POSTGRES")
class Flow(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.db=psycopg2.connect(DSN);c.db.autocommit=True
  with c.db.cursor() as x:
   x.execute("CREATE TABLE users(id SERIAL PRIMARY KEY,username TEXT,role TEXT); CREATE TABLE analytic_plans(id SERIAL PRIMARY KEY,title TEXT,course TEXT,subject TEXT,course_level TEXT,parallel TEXT,shift TEXT,teacher_id INTEGER REFERENCES users(id)); CREATE TABLE plan_topics(id SERIAL PRIMARY KEY,plan_id INTEGER REFERENCES analytic_plans(id) ON DELETE CASCADE,unit_name TEXT,topic TEXT,subtopic TEXT,learning_outcome TEXT,bloom_level TEXT,keywords TEXT); CREATE TABLE adaptive_quizzes(id SERIAL PRIMARY KEY,user_id INTEGER REFERENCES users(id),plan_id INTEGER REFERENCES analytic_plans(id),title TEXT,quiz_type TEXT,source_topic TEXT,difficulty TEXT,subject TEXT,course_level TEXT,parallel TEXT,shift TEXT,cohort TEXT,question_count INTEGER,status TEXT,score DOUBLE PRECISION,passed BOOLEAN,created_at TEXT,completed_at TEXT); CREATE TABLE adaptive_questions(id SERIAL PRIMARY KEY,quiz_id INTEGER REFERENCES adaptive_quizzes(id),question TEXT,options_json TEXT,correct_answer TEXT,position INTEGER,topic TEXT,subtopic TEXT,difficulty_level TEXT,explanation TEXT,bloom_level TEXT,user_answer TEXT,is_correct BOOLEAN,response_time_seconds DOUBLE PRECISION);")
   for n in ('019_curricular_question_bank_v1.sql','020_curricular_assessment_traceability_v2.sql'): x.execute((Path(__file__).parents[1]/'migrations'/n).read_text())
   x.execute("CREATE TABLE profiles(user_id INTEGER PRIMARY KEY,research_group TEXT); ALTER TABLE adaptive_quizzes ADD COLUMN version_code TEXT; ALTER TABLE adaptive_questions ADD COLUMN item_code TEXT; ALTER TABLE adaptive_questions ADD COLUMN dimension TEXT; ALTER TABLE adaptive_questions ADD COLUMN conceptual_error TEXT;")
  import app;c.app=app
 @classmethod
 def tearDownClass(c):c.db.close()
 def test_real_flow(self):
  a=self.app
  with self.db.cursor() as x:
   x.execute("INSERT INTO users(username,role)VALUES('t','teacher'),('a','student'),('b','student')RETURNING id");t,s1,s2=[r[0]for r in x.fetchall()]
   x.execute("INSERT INTO analytic_plans(title,course,subject,course_level,parallel,shift,teacher_id)VALUES('p','TEST-COHORT','Materia Sintética','N1','A','Nocturna',%s)RETURNING id",(t,));p=x.fetchone()[0]
   x.execute("INSERT INTO plan_topics(plan_id,unit_name,topic,subtopic,learning_outcome,bloom_level,keywords)VALUES(%s,'U','Tema Alfa','S','Resolver problemas sintéticos de Tema Alfa','Aplicar','x')RETURNING id",(p,));pt=x.fetchone()[0]
  qs=[{'question':f'Q{i}','options':['A','B','C','D'],'correct_answer':'A','explanation':'e','bloom_level':'Aplicar','difficulty_level':'Intermedio','topic':'otro'}for i in range(4)]
  class M:
   def generate_content(_,**k):return type('R',(),{'text':json.dumps(qs)})()
  a.ai_client=lambda:type('C',(),{'models':M()})()
  d=a.generate_topic_question_drafts(t,pt,'Intermedio',4);self.assertEqual(len(d),4);self.assertTrue(all(i['topic']=='Tema Alfa' and i['plan_topic_id']==pt for i in d))
  a.approve_question_bank_item(d[0]['id'],t);a.approve_question_bank_item(d[1]['id'],t);a.reject_question_bank_item(d[2]['id'],t);a.delete_question_bank_item(d[3]['id'],t)
  ok=a.get_question_bank_items(plan_id=p,status='approved');self.assertEqual(len(ok),2)
  ctx={'subject':'Materia Sintética','course_level':'N1','parallel':'A','shift':'Nocturna','cohort':'TEST-COHORT'};ass=a.create_teacher_assessment(t,p,'E',ctx);a.set_teacher_assessment_items(ass['id'],t,[i['id']for i in ok]);a.publish_teacher_assessment(ass['id'],t)
  self.assertEqual(len(a.get_student_teacher_assessments(ctx)),1);self.assertEqual(len(a.get_student_teacher_assessments({**ctx,'parallel':'B'})),0)
  q=a.start_teacher_assessment_attempt(s1,ass['id'],ctx);_,items=a.load_adaptive_quiz(q['id']);self.assertEqual(len(items),2);self.assertEqual(a.start_teacher_assessment_attempt(s1,ass['id'],ctx)['id'],q['id'])
  a.grade_teacher_assessment_attempt(q['id'],{str(items[0]['id']):'A',str(items[1]['id']):'B'});q,items=a.load_adaptive_quiz(q['id']);self.assertEqual(q['score'],50.0);self.assertTrue(a.get_teacher_assessment_curricular_analytics(ass['id'])['topic'])
  self.assertEqual(a.get_research_item_responses(),[])
  a.close_teacher_assessment(ass['id'],t)
  with self.assertRaises(ValueError):a.start_teacher_assessment_attempt(s2,ass['id'],{**ctx,'parallel':'B'})
