"""Real student navigation/controller in AppTest, synthetic external services.

Set BUNSEKI_VIEW_QA_DSN only for the marked disposable release QA database
to exercise the real PostgreSQL attempt and answer adapter as well.
"""
import ast
import os
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'app.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)
FUNCTIONS = {n.name: n for n in TREE.body if isinstance(n, ast.FunctionDef)}
ADAPTERS = {
    '_adaptive_practice_restore_active', '_adaptive_practice_hydrate_session',
    '_adaptive_practice_persist_active', '_adaptive_practice_answer_identity',
    '_adaptive_practice_answer_question_key', '_adaptive_practice_answer_widget_key',
    '_adaptive_practice_batch_key', '_adaptive_practice_autosave_answer',
    '_adaptive_practice_load_saved_answers',
}


def harness(database=False):
    common = (ROOT / 'tests/fixtures/adaptive_view_services.py').read_text(encoding='utf-8')
    names = {'student_page', 'render_student_sidebar', 'render_student_adaptive_practice',
             'adaptive_practice_next_difficulty'} | (ADAPTERS if database else {
                 '_adaptive_practice_batch_key', '_adaptive_practice_answer_identity',
                 '_adaptive_practice_answer_question_key', '_adaptive_practice_answer_widget_key'})
    code = common + '\n' + '\n'.join(ast.get_source_segment(SOURCE, FUNCTIONS[n]) for n in sorted(names))
    code += '''
import sys, json, os
sys.path.insert(0, ROOT_PATH)
BUNSEKI_FRONTEND_LOGO_DATA_URI = ''
inject_student_layout_cleanup_v2 = lambda: None
inject_bunseki_frontend_skin = lambda: None
sidebar_brand = lambda *a: None
is_official_profile = lambda p: p.get('official', False)
official_profile_ready = lambda *a: True
def get_profile(uid):
    return dict(profile_completed=True, level='Básico', first_names='Estudiante QA',
                official=st.session_state.get('qa_official', False),
                pretest_estado=st.session_state.get('qa_pretest', 'completado'),
                research_group=st.session_state.get('qa_group', 'experimental'))
academic_context_from_profile = lambda p: {}
capture_browser_gps = lambda *a, **k: None
interactions = lambda uid: []
render_student_adaptive_evaluation = lambda *a: st.info('Evaluación QA')
build_student_summary = lambda uid: ({}, pd.DataFrame())
export_student_docx = lambda uid: b'QA'
export_student_pdf = lambda uid: b'QA'
prompt_suggestions = lambda *a: []
'''.replace('ROOT_PATH', repr(str(ROOT)))
    if database:
        code += '''
import psycopg2
from psycopg2.extras import RealDictCursor
from bunseki.assessment_attempts import get_or_create_attempt as resumable_get_or_create_attempt, load_attempt_progress as resumable_load_attempt_progress, save_attempt_answer as resumable_save_attempt_answer
def conn():
    return psycopg2.connect(os.environ['BUNSEKI_VIEW_QA_DSN'])
def fetchone(sql, args=()):
    with conn() as c:
        with c.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, args)
            return cur.fetchone()
_ADAPTIVE_PRACTICE_ACTIVE_SOURCE_KEY = 'adaptive_practice:active'
'''
    return code + "\nstudent_page({'id': st.session_state.get('qa_uid', 8261), 'role':'student'})\n"


class StudentPracticeViewTests(unittest.TestCase):
    def app(self, database=False):
        app = AppTest.from_string(harness(database), default_timeout=30).run()
        self.assertFalse(app.exception)
        return app

    def navigate(self, app, page):
        app.radio(key='student_nav').set_value(page).run()
        self.assertFalse(app.exception)

    def answers(self, app):
        return [r for r in app.radio if str(r.key).startswith('practice_')]

    def test_navigation_and_permissions(self):
        app = self.app()
        self.assertEqual(self.answers(app), [])
        self.navigate(app, '🎯 Práctica adaptativa')
        self.assertEqual(len(self.answers(app)), 5)
        self.assertEqual(len(app.chat_input), 0)
        self.assertEqual(len(app.get('download_button')), 0)
        for page in ['🧠 Evaluación', '📈 Mi progreso', '📘 Descargar aprendizaje', '🎮 Prueba de nivel', '💬 Tutor']:
            self.navigate(app, page)
            self.assertEqual(self.answers(app), [])
        app.session_state['qa_official'] = True
        app.session_state['qa_pretest'] = 'pendiente'
        app.run()
        self.assertEqual(app.radio(key='student_nav').options, ['🧠 Evaluación'])
        app.session_state['qa_pretest'] = 'completado'
        app.session_state['qa_group'] = 'control'
        app.run()
        self.assertEqual(app.radio(key='student_nav').options, ['🧠 Evaluación', '📈 Mi progreso'])

    def test_mastery_review_idempotency_with_synthetic_services(self):
        app = self.app()
        app.session_state['qa_route'] = True
        self.navigate(app, '🎯 Práctica adaptativa')
        for radio in self.answers(app):
            app.radio(key=radio.key).set_value('A').run()
        for _ in range(2):
            next(b for b in app.button if b.label == 'Revisar práctica').click().run()
            self.assertFalse(app.exception)
        writes = [call for call in app.session_state['qa_trace'] if call[0] == 'record_mastery']
        self.assertEqual(len(writes), 1)

    @unittest.skipUnless(os.environ.get('BUNSEKI_VIEW_QA_DSN'), 'Disposable PostgreSQL DSN required')
    def test_postgres_navigation_session_replacement_and_round(self):
        import psycopg2
        dsn = os.environ['BUNSEKI_VIEW_QA_DSN']
        with psycopg2.connect(dsn) as c:
            self.assertEqual((c.info.host, c.info.port, c.info.dbname),
                             ('127.0.0.1', 55440, 'bunseki_release_qa'))
            with c.cursor() as cur:
                cur.execute('SELECT name FROM release_qa_marker')
                self.assertEqual(cur.fetchone()[0], 'bunseki-release-20261018')
                # Only our reserved fictional users; never truncate shared QA data.
                cur.execute('INSERT INTO users(id) VALUES (8261),(8262) ON CONFLICT DO NOTHING')
                cur.execute('DELETE FROM assessment_attempt_answers WHERE attempt_id IN (SELECT id FROM assessment_attempts WHERE user_id IN (8261,8262))')
                cur.execute('DELETE FROM assessment_attempts WHERE user_id IN (8261,8262)')
        app = self.app(True)
        self.navigate(app, '🎯 Práctica adaptativa')
        initial = [(r.key, r.label) for r in self.answers(app)]
        aid = app.session_state['adaptive_practice_attempt_id_8261']
        for radio in self.answers(app)[:3]:
            app.radio(key=radio.key).set_value('A').run()
            self.assertFalse(app.exception)
        self.navigate(app, '📈 Mi progreso')
        self.navigate(app, '🎯 Práctica adaptativa')
        self.assertEqual([(r.key, r.label) for r in self.answers(app)], initial)
        self.assertEqual([r.value for r in self.answers(app)], ['A','A','A',None,None])
        fresh = self.app(True)  # Entire AppTest session replacement, then actual menu.
        self.navigate(fresh, '🎯 Práctica adaptativa')
        self.assertEqual(fresh.session_state['adaptive_practice_attempt_id_8261'], aid)
        self.assertEqual([(r.key, r.label) for r in self.answers(fresh)], initial)
        self.assertEqual([r.value for r in self.answers(fresh)], ['A','A','A',None,None])
        other = self.app(True)
        other.session_state['qa_uid'] = 8262
        other.run()
        self.navigate(other, '🎯 Práctica adaptativa')
        self.assertNotEqual(other.session_state['adaptive_practice_attempt_id_8262'], aid)
        self.assertTrue(all(r.value is None for r in self.answers(other)))
        for radio in self.answers(fresh)[3:]:
            fresh.radio(key=radio.key).set_value('A').run()
        submit = next(b for b in fresh.button if b.label == 'Revisar práctica')
        submit.click().run()
        self.assertFalse(fresh.exception)
        state_key = 'adaptive_practice_state_8261_algebra_ecuaciones'
        self.assertIsNotNone(fresh.session_state[state_key]['result'])
        next(b for b in fresh.button if b.label == 'Revisar práctica').click().run()
        with psycopg2.connect(dsn) as c:
            with c.cursor() as cur:
                cur.execute('SELECT count(*) FROM assessment_attempt_answers WHERE attempt_id=%s', (aid,))
                self.assertEqual(cur.fetchone()[0], 5)
                cur.execute('SELECT count(*) FROM assessment_attempts WHERE user_id=8261')
                self.assertEqual(cur.fetchone()[0], 1)
        next(b for b in fresh.button if str(b.key).startswith('next_practice_')).click().run()
        self.assertFalse(fresh.exception)
        state = fresh.session_state[state_key]
        self.assertEqual(state['round'], 2)
        replacement = self.app(True)
        self.navigate(replacement, '🎯 Práctica adaptativa')
        restored = replacement.session_state[state_key]
        self.assertEqual((restored['round'], restored['difficulty']), (2, state['difficulty']))
        self.assertEqual([(r.key,r.label) for r in self.answers(replacement)],
                         [(r.key,r.label) for r in self.answers(fresh)])
        self.assertTrue(all(r.value is None for r in self.answers(replacement)))
        # Manual mode and a nondefault topic must survive widget cleanup and DB hydration.
        replacement.selectbox(key='adaptive_practice_topic_8261').set_value('Geometría').run()
        replacement.selectbox(key='adaptive_practice_level_choice_8261_geometria_triangulos').set_value('Intermedio').run()
        self.assertFalse(replacement.exception)
        manual_batch = [(r.key, r.label) for r in self.answers(replacement)]
        self.navigate(replacement, '💬 Tutor')
        self.navigate(replacement, '🎯 Práctica adaptativa')
        self.assertEqual([(r.key, r.label) for r in self.answers(replacement)], manual_batch)
        manual = self.app(True)
        self.navigate(manual, '🎯 Práctica adaptativa')
        self.assertEqual(manual.selectbox(key='adaptive_practice_topic_8261').value, 'Geometría')
        self.assertEqual(manual.selectbox(key='adaptive_practice_level_choice_8261_geometria_triangulos').value, 'Intermedio')
        self.assertEqual([(r.key, r.label) for r in self.answers(manual)], manual_batch)


if __name__ == '__main__':
    unittest.main()
