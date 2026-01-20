import threading
import time
import webbrowser

import jwt
import uvicorn

from cli.config import TOKEN_PATH

TIMEOUT_SECONDS = 120
POLL_INTERVAL = 0.5


class AuthTimeoutError(RuntimeError):
    pass


class InvalidTeamIdException(Exception):
    pass


class InvalidKeyIdException(Exception):
    pass


def generate_jwt(secret_key_file_path: str, team_id: str, key_id: str) -> str:
    """
    Generates a suitable JWT token according to the apple API. Docs: https://developer.apple.com/documentation/applemusicapi/generating-developer-tokens

    :param secret_key_file_path: Path to the p8 file.
    :param team_id: The 10 character iss registered claim key.
    :param key_id: The 10 character key identifier key.
    :return: A valid JWT string
    """
    if len(team_id) != 10:
        raise InvalidTeamIdException
    if len(key_id) != 10:
        raise InvalidKeyIdException

    current_unix_seconds = int(time.time())
    with open(secret_key_file_path, "rb") as f:
        jwt_payload = {
            "exp": current_unix_seconds + (24 * 60 * 60),  # expiration time
            "iss": team_id,  # issuer
            "iat": current_unix_seconds,  # issued at
        }

        jwt_token: str = jwt.encode(
            jwt_payload, f.read(), algorithm="ES256", headers={"kid": key_id}
        )
        return jwt_token


def start_auth_flow():
    threading.Thread(
        target=lambda: uvicorn.run(
            "server.app:app",
            host="127.0.0.1",
            port=3000,
            log_level="error",
        ),
        daemon=True,
    ).start()

    webbrowser.open("http://localhost:3000/login")
    wait_for_token()


def wait_for_token() -> str:
    """
    Block until the Music User Token is written by the auth server.

    :return: The music user token as a string.
    """
    start = time.monotonic()

    while True:
        if TOKEN_PATH.exists():
            token: str = TOKEN_PATH.read_text().strip()
            if token:
                print(token)
                return token

        if time.monotonic() - start > TIMEOUT_SECONDS:
            raise AuthTimeoutError("Timed out waiting for Apple Music authorisation.")

        time.sleep(POLL_INTERVAL)
