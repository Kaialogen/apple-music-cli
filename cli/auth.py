from time import time

import jwt


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
