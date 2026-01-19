from pathlib import Path
from typing import Any

import jwt
import pytest

from cli.auth import InvalidKeyIdException, InvalidTeamIdException, generate_jwt

"""
JWT Tests
"""
TEST_TEAM_ID = "XXXXXXXXXX"  # pragma: allowlist secret
TEST_KEY_ID = "XXXXXXXXXX"  # pragma: allowlist secret
TEST_SECRET_KEY_FILE_PATH = (
    "tests/fixtures/test_private_key.p8"  # pragma: allowlist secret
)


# Test 1: Test basic JWT shape
def test_generate_jwt_returns_string() -> None:
    token: str = generate_jwt(TEST_SECRET_KEY_FILE_PATH, TEST_TEAM_ID, TEST_KEY_ID)

    assert isinstance(token, str)
    assert token.count(".") == 2  # header.payload.signature


# Test 2: Test whether JWT headers are correct
def test_jwt_headers() -> None:
    token: str = generate_jwt(TEST_SECRET_KEY_FILE_PATH, TEST_TEAM_ID, TEST_KEY_ID)

    headers: dict[str, Any] = jwt.get_unverified_header(token)

    assert headers["alg"] == "ES256"
    assert headers["kid"] == TEST_KEY_ID


# Test 3: Tests whether JWT payload claims exist and are sane
def test_jwt_payload_claims() -> None:
    token: str = generate_jwt(TEST_SECRET_KEY_FILE_PATH, TEST_TEAM_ID, TEST_KEY_ID)

    payload = jwt.decode(
        token,
        options={"verify_signature": False},
    )

    assert payload["iss"] == TEST_TEAM_ID
    assert "iat" in payload
    assert "exp" in payload
    assert payload["exp"] > payload["iat"]


# Test 4: Tests whether JWT signature is valid
def test_jwt_signature_verifies() -> None:
    private_key: bytes = Path(TEST_SECRET_KEY_FILE_PATH).read_bytes()
    token: str = generate_jwt(TEST_SECRET_KEY_FILE_PATH, TEST_TEAM_ID, TEST_KEY_ID)

    decoded = jwt.decode(
        token,
        private_key,
        algorithms=["ES256"],
        options={"require": ["iss", "iat", "exp"]},
    )

    assert decoded["iss"] == TEST_TEAM_ID


"""
Custom Exception Tests
"""


def test_invalid_team_id_length():
    with pytest.raises(InvalidTeamIdException):
        generate_jwt(TEST_SECRET_KEY_FILE_PATH, "SHORT", TEST_KEY_ID)


def test_invalid_key_id_length():
    with pytest.raises(InvalidKeyIdException):
        generate_jwt(TEST_SECRET_KEY_FILE_PATH, TEST_TEAM_ID, "SHORT")
