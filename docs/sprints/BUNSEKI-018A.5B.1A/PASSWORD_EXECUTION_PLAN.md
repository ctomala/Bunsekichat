# Password execution plan

Founder supplies the password only into a local execution-session variable. Generate the bcrypt hash in memory using the compatible application implementation, clear the plaintext variable immediately, and pass only the hash into a wrapper located outside the repository. Never echo, log, document, or store the plaintext; remove the wrapper after execution. `PASSWORD_EXECUTION_DESIGN=PASS`.
