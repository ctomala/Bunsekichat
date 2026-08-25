import os
from pathlib import Path
import psycopg2
import pytest
from bunseki.academic import AcademicService, ValidationError

DSN=os.environ.get("BUNSEKI_TEST_DATABASE_URL")
pytestmark=pytest.mark.skipif(not DSN,reason="requires disposable PostgreSQL")

@pytest.fixture()
def db():
    c=psycopg2.connect(DSN); c.autocommit=True
    with c.cursor() as x:
        x.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public; CREATE TABLE users(id SERIAL PRIMARY KEY,username TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT,active BOOLEAN,created_at TEXT,password_temporal BOOLEAN NOT NULL DEFAULT false,primer_ingreso BOOLEAN NOT NULL DEFAULT false); CREATE TABLE profiles(user_id INTEGER PRIMARY KEY REFERENCES users(id),first_names TEXT,last_names TEXT,cedula TEXT,correo TEXT,course TEXT,parallel TEXT,cohort TEXT,teacher TEXT); CREATE TABLE interactions(id SERIAL PRIMARY KEY,user_id INTEGER REFERENCES users(id)); CREATE TABLE location_events(id SERIAL PRIMARY KEY,user_id INTEGER REFERENCES users(id),gps_lat double precision,gps_lon double precision,gps_accuracy double precision,created_at TEXT);")
        x.execute(Path("migrations/018a3_academic_foundation.sql").read_text(encoding="utf8"))
        x.execute(Path("migrations/018a5_teacher_parallel_assignments.sql").read_text(encoding="utf8"))
        x.execute("INSERT INTO users(username,password_hash,role,active,created_at) VALUES('ta','x','teacher',true,'x'),('tb','x','teacher',true,'x'),('sa','x','student',true,'x'),('sb','x','student',true,'x')")
    yield c; c.close()

def test_isolation_and_cross_course_rejection(db):
    s=AcademicService(db); ta,tb=s.create_teacher(1),s.create_teacher(2); p=s.create_period('2026-CII','x'); sub=s.create_subject('X','X'); a=s.create_course(sub,p,'A','A'); b=s.create_course(sub,p,'B','B'); s.assign_teacher(ta,a); s.assign_teacher(tb,b); pa,pb=s.create_parallel(a,'A'),s.create_parallel(b,'B'); s.assign_teacher_to_parallel(ta,pa); s.assign_teacher_to_parallel(tb,pb); ca,cb=s.create_cohort(a,'CA','CA'),s.create_cohort(b,'CB','CB'); ea=s.enroll(3,a,pa,ca); eb=s.enroll(4,b,pb,cb); assert s.teacher_can_access_enrollment(1,ea); assert not s.teacher_can_access_enrollment(1,eb); assert s.get_teacher_students(1)==[3];
    with pytest.raises(Exception): s.enroll(3,a,pb,cb)

def test_bulk_validation_rolls_back(db):
    s=AcademicService(db); p=s.create_period('2026-CII','x'); sub=s.create_subject('X','X'); c=s.create_course(sub,p,'A','A'); pa=s.create_parallel(c,'A'); co=s.create_cohort(c,'C','C')
    with pytest.raises(ValidationError): s.bulk_enroll({'course_id':c,'parallel_id':pa,'cohort_id':co},[{"student_code":"1","first_name":"A","last_name":"A","email":"a@x","username":"same"},{"student_code":"2","first_name":"B","last_name":"B","email":"b@x","username":"same"}])
    assert s._one("SELECT count(*) FROM users")[0]==4

def context(s):
    p=s.create_period('2026-CII','x'); sub=s.create_subject('X','X'); a=s.create_course(sub,p,'A','A'); b=s.create_course(sub,p,'B','B'); pa,pb=s.create_parallel(a,'A'),s.create_parallel(b,'B'); ca,cb=s.create_cohort(a,'CA','CA'),s.create_cohort(b,'CB','CB'); return a,b,pa,pb,ca,cb

def test_constraints_duplicate_and_cross_course(db):
    s=AcademicService(db); a,b,pa,pb,ca,cb=context(s); s.enroll(1,a,pa,ca)
    with pytest.raises(Exception): s.enroll(1,a,pa,ca)
    with pytest.raises(Exception): s.enroll(2,b,pa,cb)
    with pytest.raises(Exception): s.enroll(2,b,pb,ca)
    assert s._one("SELECT count(*) FROM enrollments")[0]==1

def test_bulk_valid_bcrypt_and_no_plaintext(db):
    s=AcademicService(db); a,b,pa,pb,ca,cb=context(s); rows=[{"student_code":str(i),"first_name":"F","last_name":"L","email":f"u{i}@x","username":f"u{i}"} for i in range(10)]
    created=s.bulk_enroll({'course_id':a,'parallel_id':pa,'cohort_id':ca},rows); assert len(created)==10
    password=created[0]['temporary_password']; h=s._one("SELECT password_hash FROM users WHERE id=%s",(created[0]['user_id'],))[0]
    import bcrypt; assert h != password and bcrypt.checkpw(password.encode(),h.encode())
    assert s._one("SELECT count(*) FROM users WHERE password_hash=%s",(password,))[0]==0
    assert s._one("SELECT count(*) FROM enrollments")[0]==10

def test_bulk_100_rows_is_atomic(db):
    s=AcademicService(db); a,b,pa,pb,ca,cb=context(s); rows=[{"student_code":str(i),"first_name":"F","last_name":"L","email":f"u{i}@x","username":f"u{i}"} for i in range(99)]; rows.append({"student_code":"100","first_name":"F","last_name":"L","email":"last@x","username":"u1"})
    before=[s._one(f"SELECT count(*) FROM {t}")[0] for t in ('users','profiles','enrollments')]
    with pytest.raises(ValidationError): s.bulk_enroll({'course_id':a,'parallel_id':pa,'cohort_id':ca},rows)
    assert before == [s._one(f"SELECT count(*) FROM {t}")[0] for t in ('users','profiles','enrollments')]

def test_legacy_and_gps_exact_preservation(db):
    with db.cursor() as c:
        c.execute("INSERT INTO profiles(user_id,course,parallel,cohort,teacher) VALUES(1,' legacy ',' A ',' C ',' Teacher ')" ); c.execute("INSERT INTO location_events(user_id,gps_lat,gps_lon,gps_accuracy,created_at) VALUES(1,1.1,2.2,3.3,'t'),(2,4.4,5.5,6.6,'u'),(3,7.7,8.8,9.9,'v')")
        c.execute("SELECT user_id,course,parallel,cohort,teacher FROM profiles ORDER BY user_id"); profiles=c.fetchall(); c.execute("SELECT user_id,gps_lat,gps_lon,gps_accuracy,created_at FROM location_events ORDER BY id"); gps=c.fetchall()
    assert profiles==[(1,' legacy ',' A ',' C ',' Teacher ')]
    assert gps==[(1,1.1,2.2,3.3,'t'),(2,4.4,5.5,6.6,'u'),(3,7.7,8.8,9.9,'v')]

def test_cohorts_and_deny_by_default(db):
    s=AcademicService(db); a,b,pa,pb,ca,cb=context(s); cb=s.create_cohort(a,'CB2','CB2'); ta=s.create_teacher(1); tc=s.create_teacher(2); s.assign_teacher(ta,a); s.assign_teacher_to_parallel(ta,pa); s.enroll(3,a,pa,ca); s.enroll(4,a,pa,cb)
    with db.cursor() as c: c.execute("INSERT INTO interactions(user_id) VALUES(3),(4)")
    assert s.get_cohort_students(ca)==[3] and s.get_cohort_students(cb)==[4]
    assert set(s.get_cohort_interactions(ca)).isdisjoint(set(s.get_cohort_interactions(cb)))
    assert s.get_teacher_courses(2)==[] and s.get_teacher_students(2)==[] and not s.teacher_can_access_enrollment(2,1)

def test_parallel_isolation_revoke_coteaching_and_dynamic_parallel(db):
    s=AcademicService(db); p=s.create_period('P','P'); sub=s.create_subject('Y','Y'); course=s.create_course(sub,p,'X','X')
    ta,tb,tc=s.create_teacher(1),s.create_teacher(2),s.create_teacher(3)
    for t in (ta,tb,tc): s.assign_teacher(t,course)
    a1,a2,a3=s.create_parallel(course,'A1'),s.create_parallel(course,'A2'),s.create_parallel(course,'A3')
    c1,c2,c3=s.create_cohort(course,'Y1','Y1'),s.create_cohort(course,'Y2','Y2'),s.create_cohort(course,'Y3','Y3')
    s.assign_teacher_to_parallel(ta,a1); s.assign_teacher_to_parallel(ta,a2); s.assign_teacher_to_parallel(tb,a3); s.assign_teacher_to_parallel(tc,a1)
    e1=s.enroll(3,course,a1,c1); e3=s.enroll(4,course,a3,c3)
    assert s.teacher_can_access_enrollment(1,e1) and not s.teacher_can_access_enrollment(1,e3)
    assert s.teacher_can_access_enrollment(2,e3) and not s.teacher_can_access_enrollment(2,e1)
    assert s.teacher_can_access_enrollment(3,e1) and not s.teacher_can_access_enrollment(3,e3)
    assert s.revoke_teacher_from_parallel(ta,a1)==ta and not s.teacher_can_access_enrollment(1,e1)
    a4=s.create_parallel(course,'A4'); c4=s.create_cohort(course,'Y4','Y4'); s.assign_teacher_to_parallel(tb,a4); e4=s.enroll(3,course,a4,c4)
    assert s.teacher_can_access_enrollment(2,e4) and not s.teacher_can_access_enrollment(1,e4)
