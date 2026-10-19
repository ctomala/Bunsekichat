"""Full app browser QA entry point; local marked disposable PostgreSQL only.

Run with Streamlit. Supply BUNSEKI_BROWSER_QA_DSN and BUNSEKI_BROWSER_QA_PASSWORD
outside Git. No production dotenv/secrets or external AI provider is loaded.
All application functions, login, navigation, bank allocation and persistence
remain real. Only AI generation is disabled; seed questions are deterministic.
"""
import ast
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

import psycopg2
from psycopg2.extensions import make_dsn, parse_dsn
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DSN = os.environ['BUNSEKI_BROWSER_QA_DSN']
PASSWORD = os.environ['BUNSEKI_BROWSER_QA_PASSWORD']
def validate_dsn(dsn, **kwargs):
    connection_options = {key: value for key, value in kwargs.items()
        if key not in {'cursor_factory', 'connection_factory'}}
    target = parse_dsn(make_dsn(dsn, **connection_options))
    if (target.get('host'), target.get('port'), target.get('dbname')) != (
            '127.0.0.1', '55440', 'bunseki_browser_qa_2fb'):
        raise ValueError('Browser QA requires the dedicated local disposable database.')
    if target.get('hostaddr') not in (None, '127.0.0.1'):
        raise ValueError('Browser QA forbids a non-local hostaddr override.')
    return target


validate_dsn(DSN)
connect = psycopg2.connect


def guarded_connect(dsn=None, **kwargs):
    validate_dsn(dsn or '', **kwargs)
    return connect(dsn, **kwargs)


with guarded_connect(DSN) as connection:
    with connection.cursor() as cursor:
        cursor.execute('SELECT name FROM release_qa_marker')
        if cursor.fetchone()[0] != 'bunseki-browser-qa-2fb':
            raise ValueError('The disposable browser QA marker is missing.')

os.environ['BUNSEKI_TEST_DATABASE_URL'] = DSN
os.environ['ADMIN_USER'] = 'qa_browser_admin'
os.environ['ADMIN_PASSWORD'] = PASSWORD
os.environ.pop('GEMINI_API_KEY', None)
os.environ.pop('DATABASE_URL', None)
st.secrets = {}  # No user-level or project production secrets are read.
source = (ROOT / 'app.py').read_text(encoding='utf-8')
tree = ast.parse(source)
main = tree.body.pop()
assert isinstance(main, ast.If) and '__name__' in ast.unparse(main.test)
namespace = {'__file__': str(ROOT / 'app.py'), '__name__': '__main__'}

with patch('dotenv.load_dotenv', return_value=False), patch('psycopg2.connect', guarded_connect):
    exec(compile(tree, str(ROOT / 'app.py'), 'exec'), namespace)

    @st.cache_resource
    def prepare():
        namespace['init_db']()
        with guarded_connect(DSN) as connection:
            with connection.cursor() as cursor:
                migrations = [
                    ('question_bank_items', '019_curricular_question_bank_v1.sql'),
                    ('teacher_assessments', '020_curricular_assessment_traceability_v2.sql'),
                    ('teacher_assessment_targets', '021_teacher_assessment_targeting_v3.sql'),
                    ('assessment_attempts', '021_resumable_assessment_attempts.sql'),
                    ('plan_topic_methodologies', '022_methodology_research_foundation.sql'),
                ]
                # Base init predates research_tests, referenced by migration 021.
                cursor.execute('CREATE TABLE IF NOT EXISTS research_tests(id SERIAL PRIMARY KEY)')
                for table, filename in migrations:
                    cursor.execute('SELECT to_regclass(%s)', (table,))
                    if cursor.fetchone()[0] is None:
                        cursor.execute((ROOT / 'migrations' / filename).read_text(encoding='utf-8-sig'))
                for number in (1, 2, 3, 4):
                    cursor.execute('''INSERT INTO users(username,password_hash,role,active,created_at)
                        VALUES(%s,%s,'student',true,%s) ON CONFLICT(username) DO NOTHING RETURNING id''',
                        (f'qa_estudiante_{number}', namespace['hash_password'](PASSWORD), namespace['now']()))
                    cursor.execute('SELECT id FROM users WHERE username=%s', (f'qa_estudiante_{number}',))
                    uid = cursor.fetchone()[0]
                    cursor.execute('''INSERT INTO profiles(user_id,first_names,last_names,level,
                        profile_completed,estado_dato,pretest_estado,research_group)
                        VALUES(%s,%s,'Ficticio','Básico',1,'piloto','completado','experimental')
                        ON CONFLICT(user_id) DO NOTHING''', (uid, f'Estudiante QA {number}'))
        namespace['ensure_ai_practice_supply_schema']()
        with guarded_connect(DSN) as connection:
            with connection.cursor() as cursor:
                # Numerical data differ, so the real semantic filter can allocate new rounds.
                for topic, subtopics in list(namespace['TOPICS'].items())[:2]:
                    for subtopic in subtopics[:2]:
                        for difficulty in namespace['ADAPTIVE_DIFFICULTIES']:
                            for number in range(1, 21):
                                answer = str(number * 3)
                                cursor.execute('''INSERT INTO ai_practice_question_bank(topic,subtopic,
                                    difficulty_level,question,options_json,correct_answer,explanation,
                                    bloom_level,item_code,ai_model,prompt_version,verification_status)
                                    VALUES(%s,%s,%s,%s,%s,%s,%s,'Aplicar',%s,'qa-fixture','qa-2fb','verified')
                                    ON CONFLICT(item_code) DO NOTHING''', (topic, subtopic, difficulty,
                                    f'QA ficticia {number}: calcula {number} + {number * 2}.',
                                    json.dumps([answer, str(number * 3 + 1), str(number * 3 + 2), str(number * 3 + 3)]),
                                    answer, 'Suma los dos números indicados.',
                                    f'qa2fb|{topic}|{subtopic}|{difficulty}|{number}'))
        return True

    prepare()

    def no_external_ai(*args, **kwargs):
        raise RuntimeError('QA: IA externa deshabilitada; solo banco ficticio local.')

    namespace['generate_ai_practice_bank_batch'] = no_external_ai
    namespace['ai_client'] = no_external_ai
    st.caption('QA local aislada · Estudiantes y preguntas ficticios · Sin IA externa')
    exec(compile(ast.Module(body=[main], type_ignores=[]), str(ROOT / 'app.py'), 'exec'), namespace)

    user = st.session_state.get('user')
    if user and user.get('role') == 'student':
        attempt = namespace['_adaptive_practice_restore_active'](user['id'])
        if attempt:
            with st.expander('Evidencia QA del intento (solo entorno temporal)'):
                st.json(attempt)
                st.json(namespace['_adaptive_practice_load_saved_answers'](user['id'], attempt['attempt_id']))
