"""Full application + real PostgreSQL bank/login regression, not browser automation."""
import os
from pathlib import Path
import unittest

import psycopg2
from streamlit.testing.v1 import AppTest

ENTRY = Path(__file__).with_name('qa_student_practice_browser_app.py')


@unittest.skipUnless(os.environ.get('BUNSEKI_BROWSER_QA_DSN'), 'Marked full-app QA database required')
class FullApplicationPracticeTests(unittest.TestCase):
    def run_app(self):
        app = AppTest.from_file(str(ENTRY), default_timeout=90)
        app.session_state['landing_entered'] = True
        app.run()
        self.assertFalse(app.exception)
        return app

    def login(self, app, username):
        if not any(x.key == 'lu' for x in app.text_input):
            app.button(key='landing_start').click().run()
        app.text_input(key='lu').set_value(username)
        app.text_input(key='lp').set_value(os.environ['BUNSEKI_BROWSER_QA_PASSWORD'])
        app.button(key='login_submit').click().run()
        self.assertFalse(app.exception)

    def practice(self, app):
        app.radio(key='student_nav').set_value('🎯 Práctica adaptativa').run()
        self.assertFalse(app.exception)
        return [x for x in app.radio if str(x.key).startswith('practice_')]

    def test_real_login_bank_navigation_logout_and_review(self):
        app = self.run_app()  # Creates fixtures through guarded full application bootstrap.
        dsn = os.environ['BUNSEKI_BROWSER_QA_DSN']
        with psycopg2.connect(dsn) as connection:
            self.assertEqual((connection.info.host, connection.info.port, connection.info.dbname),
                ('127.0.0.1', 55440, 'bunseki_browser_qa_2fb'))
            with connection.cursor() as cursor:
                cursor.execute('SELECT name FROM release_qa_marker')
                self.assertEqual(cursor.fetchone()[0], 'bunseki-browser-qa-2fb')
                # These two users belong exclusively to this repeatable test.
                cursor.execute("SELECT id FROM users WHERE username IN ('qa_estudiante_3','qa_estudiante_4')")
                test_users = [row[0] for row in cursor.fetchall()]
                self.assertEqual(len(test_users), 2)
                for table in ('assessment_attempts', 'ai_practice_question_serves', 'ai_practice_question_attempts'):
                    cursor.execute(f'DELETE FROM {table} WHERE user_id=ANY(%s)', (test_users,))
        self.login(app, 'qa_estudiante_3')
        uid = app.session_state['user']['id']
        self.assertEqual(len([x for x in app.radio if str(x.key).startswith('practice_')]), 0)
        self.practice(app)
        app.selectbox(key=f'adaptive_practice_topic_{uid}').set_value('Álgebra lineal').run()
        app.selectbox(key=f'adaptive_practice_subtopic_{uid}_algebra lineal').set_value('Matrices').run()
        app.selectbox(key=f'adaptive_practice_level_choice_{uid}_algebra lineal_matrices').set_value('Intermedio').run()
        self.assertFalse(app.exception)
        radios = self.practice(app)
        self.assertEqual(len(radios), 5)
        initial = [(x.key, x.label, x.options) for x in radios]
        aid = app.session_state[f'adaptive_practice_attempt_id_{uid}']
        for radio in radios[:3]:
            app.radio(key=radio.key).set_value(radio.options[0]).run()
        expected = [x.value for x in self.practice(app)]
        for page in ('💬 Tutor', '📈 Mi progreso'):
            app.radio(key='student_nav').set_value(page).run()
            self.assertFalse(app.exception)
            self.assertFalse(any(str(x.key).startswith('practice_') for x in app.radio))
        restored = self.practice(app)
        self.assertEqual([(x.key, x.label, x.options) for x in restored], initial)
        self.assertEqual([x.value for x in restored], expected)
        app.button(key='student_logout').click().run()
        self.assertNotIn('user', app.session_state)
        # AppTest retains the pre-rerun checkbox delta after session_state.clear().
        # Start a clean client after exercising the actual logout handler.
        # Same-tab logout/relogin is covered separately by the real browser run.
        app = self.run_app()
        self.login(app, 'qa_estudiante_3')
        self.assertEqual([x.value for x in self.practice(app)], expected)
        self.assertEqual(app.session_state[f'adaptive_practice_attempt_id_{uid}'], aid)
        fresh = self.run_app()
        self.login(fresh, 'qa_estudiante_3')
        self.assertEqual([x.value for x in self.practice(fresh)], expected)
        other = self.run_app()
        self.login(other, 'qa_estudiante_4')
        self.assertTrue(all(x.value is None for x in self.practice(other)))
        self.assertNotEqual(other.session_state[f"adaptive_practice_attempt_id_{other.session_state['user']['id']}"], aid)
        from bunseki import assessment_attempts as service
        other_uid = other.session_state['user']['id']
        for operation in ('load', 'save', 'resume', 'submit'):
            with self.subTest(ownership=operation), psycopg2.connect(dsn) as connection:
                with self.assertRaises(service.AttemptNotFoundError):
                    if operation == 'load':
                        service.load_attempt_progress(connection, attempt_id=aid, user_id=other_uid)
                    elif operation == 'save':
                        service.save_attempt_answer(connection, attempt_id=aid, user_id=other_uid,
                            question_key='unauthorized', answer_payload={'value': 'no'})
                    elif operation == 'resume':
                        service.resume_attempt(connection, attempt_id=aid, user_id=other_uid)
                    else:
                        service.submit_attempt(connection, attempt_id=aid, user_id=other_uid)
        for radio in self.practice(fresh)[3:]:
            fresh.radio(key=radio.key).set_value(radio.options[0]).run()
        for _ in range(2):
            next(x for x in fresh.button if x.label == 'Revisar práctica').click().run()
            self.assertFalse(fresh.exception)
        with psycopg2.connect(dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT count(*) FROM ai_practice_question_attempts WHERE user_id=%s', (uid,))
                self.assertEqual(cursor.fetchone()[0], 5)
                cursor.execute('SELECT count(*),min(elapsed_seconds),max(elapsed_seconds) FROM assessment_attempt_answers WHERE attempt_id=%s', (aid,))
                self.assertEqual(cursor.fetchone(), (5, 0, 0))
                cursor.execute('SELECT metadata_json FROM assessment_attempts WHERE id=%s', (aid,))
                metadata = cursor.fetchone()[0]
                old_batch = metadata['serve_batch_key']
        next(x for x in fresh.button if str(x.key).startswith('next_practice_')).click().run()
        self.assertFalse(fresh.exception)
        self.assertTrue(all(x.value is None for x in self.practice(fresh)))
        with psycopg2.connect(dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT metadata_json FROM assessment_attempts WHERE id=%s', (aid,))
                metadata = cursor.fetchone()[0]
                self.assertEqual((metadata['round'], metadata['difficulty'], metadata['level_choice']),
                    (2, 'Intermedio', 'Intermedio'))
                self.assertNotEqual(metadata['serve_batch_key'], old_batch)
                cursor.execute('SELECT count(*) FROM ai_practice_question_serves WHERE serve_batch_key=%s', (metadata['serve_batch_key'],))
                self.assertEqual(cursor.fetchone()[0], 5)


if __name__ == '__main__':
    unittest.main()
