"""Local QA server supervisor. Control file accepts only restart/stop.

Run outside the restricted executor when its loopback server cannot be reached
by the desktop browser. Does not execute commands from files or open the browser.
"""
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(sys.argv[1]).resolve()
WORK.mkdir(parents=True, exist_ok=True)
control = WORK / 'browser-control.txt'
status = WORK / 'browser-status.json'
generation = 0
child = None


def publish(state):
    status.write_text(json.dumps({'state': state, 'pid': child.pid if child else None,
        'generation': generation, 'port': 8531, 'time': time.time()}), encoding='utf-8')


def stop():
    if child and child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=15)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=5)


try:
    while True:
        if child is None:
            generation += 1
            with (WORK / f'browser-server-{generation}.log').open('ab') as log:
                child = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run',
                    str(ROOT / 'tests/qa_student_practice_browser_app.py'),
                    '--server.address', '127.0.0.1', '--server.port', '8531',
                    '--server.headless', 'true', '--browser.gatherUsageStats', 'false'],
                    cwd=ROOT, stdout=log, stderr=log)
            publish('running')
        if child.poll() is not None:
            publish('failed')
            break
        if control.exists():
            command = control.read_text(encoding='utf-8-sig').strip()
            control.unlink()
            if command in {'restart', 'stop'}:
                stop()
                publish('stopped')
                if command == 'stop':
                    break
                child = None
        time.sleep(1)
finally:
    stop()
