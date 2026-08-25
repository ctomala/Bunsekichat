# 5B.1B transaction package design

Precheck new post-018A.4B.1 backup, activity, conflicts, username, defective subject hex, and current aggregate baseline. In one transaction: repair all five subject names using ASCII-only PostgreSQL Unicode escapes and validate exact hex; create hashed teacher user and teacher binding; create the draft period; create five courses, five assignments, eight parallels, eight cohorts; create no enrollments. Validate all counts, codes and UTF-8 names, no plaintext password, unchanged legacy/GPS fingerprints, then commit only on PASS. Any failure rolls back.
