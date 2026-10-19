"""Login presentation; credentials and account creation stay in app.py."""
from .landing import render_intro

def render_login_intro(st, logo_uri):
    render_intro(st, logo_uri, login=True)
