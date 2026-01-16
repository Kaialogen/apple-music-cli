import os
from time import time
from typing import cast

import jwt
import requests
from dotenv import load_dotenv

load_dotenv()


class InvalidTeamIdException(Exception):
    pass


class InvalidKeyIdException(Exception):
    pass


TEAM_ID: str | None = os.getenv("APPLE_MUSIC_TEAM_ID")
KEY_ID: str | None = os.getenv("APPLE_MUSIC_KEY_ID")
PRIVATE_KEY_PATH: str | None = os.getenv("APPLE_MUSIC_PRIVATE_KEY_PATH")

if not all([TEAM_ID, KEY_ID, PRIVATE_KEY_PATH]):
    raise RuntimeError(
        "Missing Apple Music credentials. "
        "Set APPLE_MUSIC_TEAM_ID, APPLE_MUSIC_KEY_ID, "
        "and APPLE_MUSIC_PRIVATE_KEY_PATH."
    )


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

    current_unix_seconds = int(time())
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


def get_data(url: str, jwt: str) -> None:
    headers: dict[str, str] = {"Authorization": "Bearer " + jwt}
    response: requests.Response = requests.get(url, headers=headers)
    print(response.json())


def main():
    key_id: str = cast(str, KEY_ID)
    team_id: str = cast(str, TEAM_ID)
    secret_key_file_path: str = cast(str, PRIVATE_KEY_PATH)
    url: str = "https://api.music.apple.com/v1/catalog/us/songs/203709340"

    jwt: str = generate_jwt(secret_key_file_path, team_id, key_id)

    get_data(url, jwt)


if __name__ == "__main__":
    main()
