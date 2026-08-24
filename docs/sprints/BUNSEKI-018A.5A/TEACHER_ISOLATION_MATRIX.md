# Teacher isolation matrix

Authorization is derived only through `teachers.user_id → teacher_courses.course_id → enrollments.course_id`. Absence of a matching assignment denies access. Legacy text and a broad application admin role are not a substitute for this authorization path.

| Resource | Authorized condition | Denied condition |
|---|---|---|
| course | teacher has matching `teacher_courses` row | no matching assignment |
| parallel | parallel belongs to an assigned course | any other course |
| cohort | cohort belongs to an assigned course | any other course |
| enrollment | enrollment belongs to an assigned course | no matching course assignment |
| student analytics | each student has an enrollment in an assigned course | unmatched student/course |
| GPS-derived analytics | same enrollment scope plus approved derived-only analysis | exact coordinates or unmatched course |
| research exports | assigned course, approved cohort, consent/governance checks | absent assignment or governance approval |
| question performance | assigned course and enrolled student scope | absent assignment |

The service tests and synthetic transaction demonstrate course-scoped deny-by-default behavior. App integration is explicitly out of scope; it must not be declared isolated until it applies this matrix.
