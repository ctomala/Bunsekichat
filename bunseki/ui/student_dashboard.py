"""Student presentation only. Practice stays in the existing controller."""
from html import escape
from .theme import stylesheet_html
from .icons import icon_container
from .cards import information

# Reserved presentation terminology for Phase 2F; no active route or control.
PRACTICE_VIEW_LABEL = "Práctica adaptativa"
STUDENT_CSS = '<style>\nbody:has(.bui-student-surface) .bui-student-surface{background:white;color:#173052;border:1px solid #E6EAF2;border-left:5px solid #DF73A0;border-radius:18px;padding:clamp(16px,3vw,28px);box-shadow:0 5px 18px rgba(23,48,82,.06);margin-bottom:24px;}\nbody:has(.bui-student-surface) .bui-student-surface h1{color:#173052;font-size:clamp(24px,3vw,36px);line-height:1.25;margin:16px 0;overflow-wrap:anywhere;}\nbody:has(.bui-student-surface) .bui-student-logo{display:block;width:min(280px,100%);height:auto;}\nbody:has(.bui-student-surface) .bui-student-detail{display:flex;flex-wrap:wrap;gap:12px;color:#526175;}\nbody:has(.bui-student-surface) :is(.metric,.card,.saas-help-card){background:white!important;color:#173052!important;border:1px solid #E6EAF2!important;border-left:5px solid #33836A!important;border-radius:18px!important;padding:18px!important;box-shadow:0 5px 18px rgba(23,48,82,.06)!important;overflow-wrap:anywhere;}\nbody:has(.bui-student-surface) .metric{min-height:105px;}\nbody:has(.bui-student-surface) .metric b{color:#173052;font-size:26px;}\nbody:has(.bui-student-surface) .saas-help-card{border-left-color:#D6A12D!important;}\nbody:has(.bui-student-surface) .card{border-left-color:#4C86DB!important;}\nbody:has(.bui-student-surface) .st-key-student_assessment_shortcut button{background:#DF73A0!important;color:#102642!important;border:1px solid #173052!important;min-height:44px;}\nbody:has(.bui-student-surface) [data-testid="stSidebar"]{background:#F6F8FC;}\nbody:has(.bui-student-surface) [data-testid="stSidebar"] [data-testid="stRadio"] label{background:white;border-left:4px solid #4C86DB;border-radius:10px;padding:8px;min-height:44px;}\nbody:has(.bui-student-surface) [data-testid="stSidebar"] button{min-height:44px;color:#173052;border:1px solid #E6EAF2;border-radius:10px;}\nbody:has(.bui-student-surface) .st-key-student_assessment_shortcut button:focus-visible,body:has(.bui-student-surface) [data-testid="stSidebar"] :is(button,input,[role="combobox"]):focus-visible{outline:3px solid #173052!important;outline-style:solid!important;outline-offset:3px;}\n@media(max-width:768px){body:has(.bui-student-surface) [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;}body:has(.bui-student-surface) [data-testid="stMainBlockContainer"] [data-testid="stColumn"]{width:100%!important;flex:1 1 100%!important;min-width:0!important;}}\n\nbody:has(.bui-student-surface) [data-testid="stMainBlockContainer"]{padding-top:4.5rem!important;}\nbody:has(.bui-student-surface) [data-testid="stSidebar"] .bunseki-sidebar-brand-v2{background:white!important;border-color:#E6EAF2!important;border-left:4px solid #8462C3!important;box-shadow:0 5px 18px rgba(23,48,82,.06)!important;}\nbody:has(.bui-student-surface) [data-testid="stSidebar"] .bunseki-sidebar-role-v2{background:#DF73A0!important;color:#102642!important;box-shadow:none!important;}\n</style>'

# Current Streamlit places the reopen button inside stToolbar. Legacy app CSS
# hides that parent, so making the button visible alone cannot restore access.
SIDEBAR_RECOVERY_CSS = '''<style>
body:has(.bui-student-surface) [data-testid="stToolbar"]:has([data-testid="stExpandSidebarButton"]){display:flex!important;}
body:has(.bui-student-surface) [data-testid="stSidebarCollapseButton"],
body:has(.bui-student-surface) [data-testid="stSidebarCollapseButton"] button{visibility:visible!important;}
body:has(.bui-student-surface) :is([data-testid="stToolbarActions"],[data-testid="stAppDeployButton"],[data-testid="stMainMenu"]){display:none!important;}
</style>'''


def render_student_header(st, logo_uri, first_names, subject, level, cohort):
    text=lambda value: escape(str(value if value is not None else ""), quote=True)
    st.html(stylesheet_html() + STUDENT_CSS + SIDEBAR_RECOVERY_CSS)
    greeting = "Bienvenido/a" + (", " + text(first_names) if first_names else "")
    st.markdown('<header class="bunseki-ui bui-student-surface"><img class="bui-student-logo" src="' + text(logo_uri) + '" alt="BunsekiChat">' + icon_container("home") + '<h1>' + greeting + '</h1><div class="bui-student-detail"><span>' + text(subject) + '</span><span>Nivel: ' + text(level) + '</span><span>' + text(cohort) + '</span></div></header>', unsafe_allow_html=True)
    st.markdown(information("Continúa con las opciones disponibles para tu perfil académico."), unsafe_allow_html=True)
