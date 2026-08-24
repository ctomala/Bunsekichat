# GPS privacy audit

`interactions` contains 734 records: 341 have latitude/longitude/accuracy and 393 do not. `location_events` contains 937 records, all with coordinates, accuracy and timestamp. Both join to `users.id`; their coordinates are `double precision`. `app.py` renders heatmaps, individual points, tables and CSV exports for the teacher dashboard.

GPS was not read at row level, changed or exported during this audit. Future schema must preserve `user_id` links and add optional `enrollment_id` only for newly captured events. Operational coordinates remain restricted; research exports must use derived bands/zones/clusters and exclude exact coordinates by default.
