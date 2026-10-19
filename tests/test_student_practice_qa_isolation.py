"""The browser QA harness must reject other destinations before connecting."""
import ast
from pathlib import Path
import unittest

from psycopg2.extensions import make_dsn, parse_dsn

tree = ast.parse(Path(__file__).with_name('qa_student_practice_browser_app.py').read_text(encoding='utf-8'))
node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_dsn')
namespace = dict(make_dsn=make_dsn, parse_dsn=parse_dsn)
exec(compile(ast.Module(body=[node], type_ignores=[]), 'QA destination validator', 'exec'), namespace)
validate = namespace['validate_dsn']
LOCAL = 'host=127.0.0.1 port=55440 dbname=bunseki_browser_qa_2fb'


class BrowserQADestinationTests(unittest.TestCase):
    def test_accepts_only_explicit_local_target(self):
        self.assertEqual(validate(LOCAL, cursor_factory=object)['dbname'], 'bunseki_browser_qa_2fb')

    def test_rejects_destination_overrides_before_connecting(self):
        for overrides in ({'host': 'production.invalid'}, {'port': 5432},
                          {'database': 'bunseki_test'}, {'hostaddr': '192.0.2.1'}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                validate(LOCAL, **overrides)


if __name__ == '__main__':
    unittest.main()
