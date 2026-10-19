"""Synthetic question/mastery providers; persistence is injected by the test."""
import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib,unicodedata,copy
TOPICS={"Álgebra":["Ecuaciones","Funciones"],"Geometría":["Triángulos","Áreas"]}
ADAPTIVE_DIFFICULTIES=["Inicial","Básico","Intermedio","Avanzado"]
PRACTICE_LEVEL_HELP={};PRACTICE_LEVEL_LABELS={}
def trace(name,*args,**kwargs):st.session_state.setdefault('qa_trace',[]).append(copy.deepcopy((name,args,kwargs)))
def strip_accents(value):return ''.join(c for c in unicodedata.normalize('NFD',str(value)) if unicodedata.category(c)!='Mn')
def normalize_adaptive_difficulty(value):return value if value in ADAPTIVE_DIFFICULTIES else 'Básico'
def fixture_items(topic='Álgebra',subtopic='Funciones',difficulty='Básico',round_no=1):return [{'item_code':f'qa{round_no}-{i}','question':f'Pregunta ficticia {i}', 'options':['A','B','C','D'],'correct_answer':'A','explanation':'Explicación QA','topic':topic,'subtopic':subtopic,'bloom_level':'Aplicar'} for i in range(5)]
def _adaptive_practice_hydrate_session(user):
    trace('hydrate',user)
    st.session_state.setdefault('adaptive_practice_db_restore_checked_71',True)
    st.session_state.setdefault('adaptive_practice_attempt_id_71',501)
def get_student_approved_mbada_methodologies(prof):
    trace('approved',prof)
    return [{'id':9,'plan_topic_id':19,'topic':'Álgebra','subtopic':'Funciones','mastery_threshold':80,'learning_outcome':'QA'}] if st.session_state.get('qa_route') else []
def get_student_topic_mastery(*args):
    trace('mastery',*args)
    return {'mastery_score':80,'retrieval_count':2,'mastery_state':'proficient'} if st.session_state.get('qa_reconcile') else None
def get_student_latest_route_practice_difficulty(*args):trace('latest_difficulty',*args);return 'Básico'
def adaptive_practice_questions(uid,topic,difficulty,**kwargs):
    trace('questions',uid,topic,difficulty,**kwargs)
    if st.session_state.get('qa_generation_error'):raise RuntimeError('QA unavailable')
    return fixture_items(topic,kwargs['current_subtopic'],difficulty,kwargs['round_no'])
def _adaptive_practice_persist_active(*args):trace('persist',*args)
def _adaptive_practice_restore_active(uid):trace('restore',uid);return {'attempt_id':501}
def _adaptive_practice_load_saved_answers(uid,aid):
    trace('answers',uid,aid)
    if not st.session_state.get('qa_saved'):return {}
    state=next(v for k,v in st.session_state.items() if k.startswith('adaptive_practice_state_'))
    batch=_adaptive_practice_batch_key(uid,'Álgebra','Funciones',state['difficulty'],state['round'])
    return {_adaptive_practice_answer_question_key(item,batch):{'answer_json':{'value':'A'}} for item in state['items']}
def _adaptive_practice_autosave_answer(*args):trace('autosave',*args,value=st.session_state[args[4]])
def stable_item_code(question):return hashlib.sha256(question.encode()).hexdigest()[:16]
def record_ai_practice_bank_results_batch(records):trace('bank_results',records)
def record_student_mbada_practice_result(*args):
    trace('record_mastery',*args)
    if st.session_state.get('qa_mastery_error'):raise RuntimeError('QA mastery unavailable')
    return {'id':12,'mastery_state':'mastered','mastery_score':100,'mastery_threshold':80,'attempts_count':1,'correct_count':5}
def log_location_event(*args,**kwargs):trace('location',*args,**kwargs)
def adaptive_learning_prompts(*args):trace('prompts',*args);return ['QA consolidación']
