"""PostgreSQL-only academic foundation; no production connection is created here."""
from __future__ import annotations

import secrets
import string
import bcrypt


class ValidationError(ValueError): pass
class AuthorizationDenied(PermissionError): pass

class AcademicService:
    def __init__(self, connection): self.connection = connection
    def _one(self, sql, params=()):
        with self.connection.cursor() as c: c.execute(sql, params); return c.fetchone()
    def create_teacher(self, user_id):
        return self._one("INSERT INTO teachers(user_id) VALUES(%s) RETURNING id", (user_id,))[0]
    def create_period(self, code, name): return self._one("INSERT INTO academic_periods(code,name) VALUES(%s,%s) RETURNING id", (code,name))[0]
    def create_subject(self, code, name): return self._one("INSERT INTO subjects(code,name) VALUES(%s,%s) RETURNING id", (code,name))[0]
    def create_course(self, subject_id, period_id, code, name): return self._one("INSERT INTO courses(subject_id,academic_period_id,code,name) VALUES(%s,%s,%s,%s) RETURNING id",(subject_id,period_id,code,name))[0]
    def assign_teacher(self, teacher_id, course_id): self._one("INSERT INTO teacher_courses(teacher_id,course_id) VALUES(%s,%s) RETURNING teacher_id",(teacher_id,course_id))
    def create_parallel(self, course_id, code, name=None): return self._one("INSERT INTO parallels(course_id,code,name) VALUES(%s,%s,%s) RETURNING id",(course_id,code,name or code))[0]
    def create_cohort(self, course_id, code, name): return self._one("INSERT INTO cohorts(course_id,code,name) VALUES(%s,%s,%s) RETURNING id",(course_id,code,name))[0]
    def enroll(self, student_user_id, course_id, parallel_id, cohort_id, source="manual"):
        return self._one("INSERT INTO enrollments(student_user_id,course_id,parallel_id,cohort_id,source) VALUES(%s,%s,%s,%s,%s) RETURNING id",(student_user_id,course_id,parallel_id,cohort_id,source))[0]
    def teacher_can_access_enrollment(self, teacher_user_id, enrollment_id):
        return bool(self._one("SELECT 1 FROM enrollments e JOIN teacher_courses tc ON tc.course_id=e.course_id JOIN teachers t ON t.id=tc.teacher_id WHERE t.user_id=%s AND e.id=%s",(teacher_user_id,enrollment_id)))
    def get_teacher_students(self, teacher_user_id):
        with self.connection.cursor() as c:
            c.execute("SELECT DISTINCT e.student_user_id FROM enrollments e JOIN teacher_courses tc ON tc.course_id=e.course_id JOIN teachers t ON t.id=tc.teacher_id WHERE t.user_id=%s ORDER BY 1",(teacher_user_id,)); return [r[0] for r in c.fetchall()]
    def get_teacher_courses(self, teacher_user_id):
        with self.connection.cursor() as c:
            c.execute("SELECT c.id FROM courses c JOIN teacher_courses tc ON tc.course_id=c.id JOIN teachers t ON t.id=tc.teacher_id WHERE t.user_id=%s ORDER BY 1",(teacher_user_id,)); return [r[0] for r in c.fetchall()]
    def get_cohort_students(self, cohort_id):
        with self.connection.cursor() as c:
            c.execute("SELECT student_user_id FROM enrollments WHERE cohort_id=%s ORDER BY student_user_id",(cohort_id,)); return [r[0] for r in c.fetchall()]
    def get_cohort_interactions(self, cohort_id):
        with self.connection.cursor() as c:
            c.execute("SELECT i.id FROM interactions i JOIN enrollments e ON e.student_user_id=i.user_id WHERE e.cohort_id=%s ORDER BY i.id",(cohort_id,)); return [r[0] for r in c.fetchall()]
    def get_teacher_interactions(self, teacher_user_id):
        with self.connection.cursor() as c:
            c.execute("SELECT i.id FROM interactions i JOIN enrollments e ON e.student_user_id=i.user_id JOIN teacher_courses tc ON tc.course_id=e.course_id JOIN teachers t ON t.id=tc.teacher_id WHERE t.user_id=%s",(teacher_user_id,)); return [r[0] for r in c.fetchall()]
    def bulk_enroll(self, context, rows):
        required={"student_code","first_name","last_name","email","username"}
        errors=[]; seen_usernames=set(); seen_emails=set(); seen_codes=set()
        for n,row in enumerate(rows,1):
            missing=required-set(row)
            key=(row.get("username","" ).strip().lower(),row.get("email","" ).strip().lower(),row.get("student_code","" ).strip())
            username,email,code=key
            if missing or not all(key) or username in seen_usernames or email in seen_emails or code in seen_codes: errors.append(n)
            seen_usernames.add(username); seen_emails.add(email); seen_codes.add(code)
        if errors: raise ValidationError(f"invalid import rows: {errors}")
        with self.connection.cursor() as c:
            c.execute("SELECT p.course_id, p.id, c.id FROM parallels p JOIN cohorts c ON c.course_id=p.course_id WHERE p.id=%s AND c.id=%s",(context["parallel_id"],context["cohort_id"])); valid=c.fetchone()
            if not valid or valid[0] != context["course_id"]: raise ValidationError("academic context mismatch")
            for row in rows:
                c.execute("SELECT 1 FROM users WHERE username=%s",(row["username"].strip().lower(),))
                if c.fetchone(): raise ValidationError("username already exists")
                c.execute("SELECT 1 FROM profiles WHERE lower(correo)=lower(%s) OR cedula=%s",(row["email"].strip(),row["student_code"].strip()))
                if c.fetchone(): raise ValidationError("student already exists")
            created=[]
            for row in rows:
                password="".join(secrets.choice(string.ascii_letters+string.digits) for _ in range(16))
                hashed=bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
                c.execute("INSERT INTO users(username,password_hash,role,active,created_at,password_temporal,primer_ingreso) VALUES(%s,%s,%s,true,now()::text,true,true) RETURNING id",(row["username"].strip().lower(),hashed,"student")); uid=c.fetchone()[0]
                c.execute("INSERT INTO profiles(user_id,first_names,last_names,cedula,correo) VALUES(%s,%s,%s,%s,%s)",(uid,row["first_name"],row["last_name"],row["student_code"],row["email"]))
                c.execute("INSERT INTO enrollments(student_user_id,course_id,parallel_id,cohort_id,source) VALUES(%s,%s,%s,%s,%s)",(uid,context["course_id"],context["parallel_id"],context["cohort_id"],"bulk_import")); created.append({"user_id":uid,"username":row["username"],"temporary_password":password})
        return created
