# Test strategy

Add local pytest tests around a data-access/service layer before changing `app.py`: catalog uniqueness; teacher creation; course/cohort hierarchy; enrollment uniqueness/history; import prevalidation and transaction rollback; teacher deny-by-default scope; legacy profile fallback; credential hashing/first-login; analytics scope filters; GPS preservation; and research de-identification. Use an isolated PostgreSQL test database or disposable schema, never Supabase production. Add a Streamlit smoke check after service tests.
