# Subject display-name encoding incident

`SOURCE_FILE_UTF8=PASS`: byte inspection of `018a3_academic_foundation.sql` matched the exact UTF-8 bytes for all five Spanish display names. Production read-only evidence certifies `SUBJECT_ENCODING_DEFECT=CONFIRMED` in all five stored names, while codes remain correct.

The defect is limited to newly seeded subject display names; codes, relationships, and legacy/GPS content have no observed corruption. Root cause is therefore **post-source Unicode transport/client encoding corruption**. The available evidence rules out the source migration but does not distinguish PowerShell text handling, PowerShell-to-native piping, or client encoding; no more specific attribution is asserted.
