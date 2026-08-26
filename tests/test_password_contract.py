import unittest

from bunseki.academic import service
from bunseki.security.passwords import (
    hash_password,
    safe_password,
    verify_password,
)


class PasswordContractTests(unittest.TestCase):

    def test_academic_service_uses_canonical_password_helper(self):
        self.assertIs(service.hash_password, hash_password)

    def test_temporary_password_roundtrip(self):
        password = "StudentA9x7K2m4P6q8"

        password_hash = service.hash_password(password)

        self.assertTrue(password_hash.startswith("$2"))
        self.assertTrue(verify_password(password, password_hash))
        self.assertFalse(
            verify_password(password + "_wrong", password_hash)
        )

    def test_unicode_password_roundtrip(self):
        password = "Matemática-Álgebra-Ñ-2026"

        password_hash = service.hash_password(password)

        self.assertTrue(verify_password(password, password_hash))
        self.assertFalse(
            verify_password("otra-contraseña", password_hash)
        )

    def test_long_password_roundtrip(self):
        password = "X" * 200

        password_hash = service.hash_password(password)

        self.assertEqual(len(safe_password(password)), 32)
        self.assertTrue(verify_password(password, password_hash))
        self.assertFalse(
            verify_password(("X" * 199) + "Y", password_hash)
        )

    def test_invalid_hash_fails_closed(self):
        self.assertFalse(verify_password("password", ""))
        self.assertFalse(
            verify_password("password", "not-a-bcrypt-hash")
        )


if __name__ == "__main__":
    unittest.main()