"""Tests for security utilities."""

from aios.core.security import (
    create_access_token,
    decode_access_token,
    generate_api_key,
    generate_secret_key,
    get_password_hash,
    hash_data,
    sanitize_input,
    secure_compare,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        hash1 = get_password_hash("password1")
        hash2 = get_password_hash("password2")

        assert hash1 != hash2


class TestJWT:
    """Test JWT token functions."""

    def test_create_and_decode_token(self):
        """Test creating and decoding JWT tokens."""
        data = {"sub": "user123", "role": "admin"}
        token = create_access_token(data)

        assert isinstance(token, str)

        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["role"] == "admin"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        result = decode_access_token("invalid.token.here")
        assert result is None

    def test_token_expiration(self):
        """Test token expiration is set."""
        from datetime import timedelta

        data = {"sub": "user123"}
        token = create_access_token(data, expires_delta=timedelta(hours=1))
        decoded = decode_access_token(token)

        assert decoded is not None
        assert "exp" in decoded
        assert "iat" in decoded


class TestGenerators:
    """Test generator functions."""

    def test_generate_secret_key(self):
        """Test secret key generation."""
        key1 = generate_secret_key()
        key2 = generate_secret_key()

        assert len(key1) == 128  # 64 bytes hex encoded
        assert key1 != key2

    def test_generate_api_key(self):
        """Test API key generation."""
        key = generate_api_key()

        assert key.startswith("aios_")
        assert len(key) > 20

    def test_hash_data(self):
        """Test data hashing."""
        data = "test_data"
        hash1 = hash_data(data)
        hash2 = hash_data(data)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex digest


class TestSecureCompare:
    """Test secure comparison."""

    def test_equal_strings(self):
        """Test comparison of equal strings."""
        assert secure_compare("test", "test")

    def test_different_strings(self):
        """Test comparison of different strings."""
        assert not secure_compare("test1", "test2")


class TestSanitize:
    """Test input sanitization."""

    def test_remove_null_bytes(self):
        """Test null byte removal."""
        result = sanitize_input("test\x00data")
        assert "\x00" not in result

    def test_strip_control_characters(self):
        """Test control character stripping."""
        result = sanitize_input("test\x01\x02data")
        assert "\x01" not in result
        assert "\x02" not in result

    def test_preserve_newlines(self):
        """Test that newlines are preserved."""
        result = sanitize_input("line1\nline2")
        assert "\n" in result

    def test_strip_whitespace(self):
        """Test whitespace stripping."""
        result = sanitize_input("  test  ")
        assert result == "test"
