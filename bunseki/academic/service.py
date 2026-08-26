"""PostgreSQL-only academic foundation; no production connection is created here."""
from __future__ import annotations

import secrets
import string
from bunseki.security.passwords import hash_password

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
    def assign_teacher_to_parallel(self, teacher_id, parallel_id):
        row=self._one("SELECT p.course_id FROM parallels p WHERE p.id=%s",(parallel_id,))
        if not row or not self._one("SELECT 1 FROM teacher_courses WHERE teacher_id=%s AND course_id=%s",(teacher_id,row[0])): raise ValidationError("teacher is not assigned to parallel course")
        return self._one("INSERT INTO teacher_parallels(teacher_id,parallel_id) VALUES(%s,%s) RETURNING teacher_id",(teacher_id,parallel_id))[0]
    def revoke_teacher_from_parallel(self, teacher_id, parallel_id):
        row=self._one("DELETE FROM teacher_parallels WHERE teacher_id=%s AND parallel_id=%s RETURNING teacher_id",(teacher_id,parallel_id))
        return row[0] if row else None
    def create_parallel(self, course_id, code, name=None): return self._one("INSERT INTO parallels(course_id,code,name) VALUES(%s,%s,%s) RETURNING id",(course_id,code,name or code))[0]
    def create_cohort(self, course_id, parallel_id, code, name):
        if not self._one("SELECT 1 FROM parallels WHERE id=%s AND course_id=%s",(parallel_id,course_id)):
            raise ValidationError("parallel does not belong to the requested course")
        return self._one("INSERT INTO cohorts(course_id,parallel_id,code,name) VALUES(%s,%s,%s,%s) RETURNING id",(course_id,parallel_id,code,name))[0]
    def enroll(self, student_user_id, course_id, parallel_id, cohort_id, source="manual"):
        return self._one("INSERT INTO enrollments(student_user_id,course_id,parallel_id,cohort_id,source) VALUES(%s,%s,%s,%s,%s) RETURNING id",(student_user_id,course_id,parallel_id,cohort_id,source))[0]
    def teacher_can_access_enrollment(self, teacher_user_id, enrollment_id):
        return bool(self._one("SELECT 1 FROM enrollments e JOIN teacher_parallels tp ON tp.parallel_id=e.parallel_id JOIN teachers t ON t.id=tp.teacher_id WHERE t.user_id=%s AND e.id=%s",(teacher_user_id,enrollment_id)))
    def get_teacher_students(self, teacher_user_id):
        with self.connection.cursor() as c:
            c.execute("SELECT DISTINCT e.student_user_id FROM enrollments e JOIN teacher_parallels tp ON tp.parallel_id=e.parallel_id JOIN teachers t ON t.id=tp.teacher_id WHERE t.user_id=%s ORDER BY 1",(teacher_user_id,)); return [r[0] for r in c.fetchall()]
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
            c.execute("SELECT i.id FROM interactions i JOIN enrollments e ON e.student_user_id=i.user_id JOIN teacher_parallels tp ON tp.parallel_id=e.parallel_id JOIN teachers t ON t.id=tp.teacher_id WHERE t.user_id=%s",(teacher_user_id,)); return [r[0] for r in c.fetchall()]
    def _assert_teacher_bulk_scope(self, cursor, teacher_user_id, context):
        if not teacher_user_id:
            raise ValidationError("teacher identity is required")
        required_context={"course_id","parallel_id","cohort_id"}
        if not isinstance(context,dict) or not required_context.issubset(context):
            raise ValidationError("incomplete academic context")
        cursor.execute("SELECT 1 FROM teachers t JOIN teacher_courses tc ON tc.teacher_id=t.id JOIN teacher_parallels tp ON tp.teacher_id=t.id JOIN parallels p ON p.id=tp.parallel_id WHERE t.user_id=%s AND tc.course_id=%s AND tp.parallel_id=%s AND p.course_id=%s LIMIT 1",(teacher_user_id,context["course_id"],context["parallel_id"],context["course_id"]))
        if not cursor.fetchone():
            raise ValidationError("teacher is not assigned to the requested parallel")

    def bulk_enroll(self, context, rows, teacher_user_id=None):
        required_context={"course_id","parallel_id","cohort_id"}
        if not isinstance(context,dict) or not required_context.issubset(context):
            raise ValidationError("incomplete academic context")
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
            own_transaction=bool(self.connection.autocommit)
            savepoint=f"bunseki_bulk_{secrets.token_hex(8)}"

            if own_transaction:
                c.execute("BEGIN")
            else:
                c.execute(f"SAVEPOINT {savepoint}")

            try:
                if teacher_user_id is not None:
                    self._assert_teacher_bulk_scope(c,teacher_user_id,context)

                c.execute("SELECT 1 FROM cohorts co JOIN parallels p ON p.id=co.parallel_id AND p.course_id=co.course_id WHERE co.id=%s AND co.course_id=%s AND co.parallel_id=%s AND p.id=%s AND p.course_id=%s",(context["cohort_id"],context["course_id"],context["parallel_id"],context["parallel_id"],context["course_id"]))
                if not c.fetchone(): raise ValidationError("academic context mismatch")

                for row in rows:
                    c.execute("SELECT 1 FROM users WHERE username=%s",(row["username"].strip().lower(),))
                    if c.fetchone(): raise ValidationError("username already exists")
                    c.execute("SELECT 1 FROM profiles WHERE lower(correo)=lower(%s) OR cedula=%s",(row["email"].strip(),row["student_code"].strip()))
                    if c.fetchone(): raise ValidationError("student already exists")

                created=[]
                for row in rows:
                    password="".join(secrets.choice(string.ascii_letters+string.digits) for _ in range(16))
                    hashed=hash_password(password)
                    c.execute("INSERT INTO users(username,password_hash,role,active,created_at,password_temporal,primer_ingreso) VALUES(%s,%s,%s,true,now()::text,true,true) RETURNING id",(row["username"].strip().lower(),hashed,"student"))
                    uid=c.fetchone()[0]
                    c.execute("INSERT INTO profiles(user_id,first_names,last_names,cedula,correo) VALUES(%s,%s,%s,%s,%s)",(uid,row["first_name"],row["last_name"],row["student_code"],row["email"]))
                    c.execute("INSERT INTO enrollments(student_user_id,course_id,parallel_id,cohort_id,source) VALUES(%s,%s,%s,%s,%s)",(uid,context["course_id"],context["parallel_id"],context["cohort_id"],"bulk_import"))
                    created.append({"user_id":uid,"username":row["username"],"temporary_password":password})

                if own_transaction:
                    c.execute("COMMIT")
                else:
                    c.execute(f"RELEASE SAVEPOINT {savepoint}")

            except Exception:
                if own_transaction:
                    c.execute("ROLLBACK")
                else:
                    c.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                    c.execute(f"RELEASE SAVEPOINT {savepoint}")
                raise

        return created

    def bulk_enroll_for_teacher(self, teacher_user_id, context, rows):
        if not teacher_user_id:
            raise ValidationError("teacher identity is required")
        return self.bulk_enroll(context,rows,teacher_user_id=teacher_user_id)
