# Historical reconciliation policy

No historical profile is automatically backfilled. `legacy_academic_reconciliation` currently provides `user_id` (unique), optional `enrollment_id`, free-text `status`, and optional `reason`; it has no database status vocabulary. This phase sets the operational vocabulary without changing schema:

| Status | Objective criterion | Action |
|---|---|---|
| SAFE_TO_LINK | every required identity and academic identifier independently verified and unambiguous | eligible for a separately approved manual-link batch; no automatic write |
| INCOMPLETE | one or more required identifiers absent | retain legacy, request evidence |
| NEEDS_MANUAL_REVIEW | values exist but conflict, vary, or map to multiple possible records | hold for human review |
| REJECTED | evidence is inconsistent or cannot be validated | retain legacy with documented reason |
| RESOLVED | Founder or authorized teacher manually approved a specific relationship | may receive an explicit authorized enrollment |

Legacy free text, including teacher, subject, course, parallel, cohort, level, and research group, cannot establish an academic period or authorization. The reconciliation row is an audit aid, not an implicit enrollment. `AUTOMATIC_HISTORICAL_BACKFILL=NO`.
