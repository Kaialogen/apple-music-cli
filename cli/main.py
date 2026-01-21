import os
from typing import cast

import requests
from dotenv import load_dotenv

from cli.auth import generate_jwt, start_auth_flow
from cli.config import TOKEN_PATH

load_dotenv()


TEAM_ID: str | None = os.getenv("APPLE_MUSIC_TEAM_ID")
KEY_ID: str | None = os.getenv("APPLE_MUSIC_KEY_ID")
PRIVATE_KEY_PATH: str | None = os.getenv("APPLE_MUSIC_PRIVATE_KEY_PATH")

if not all([TEAM_ID, KEY_ID, PRIVATE_KEY_PATH]):
    raise RuntimeError(
        "Missing Apple Music credentials. "
        "Set APPLE_MUSIC_TEAM_ID, APPLE_MUSIC_KEY_ID, "
        "and APPLE_MUSIC_PRIVATE_KEY_PATH."
    )


def get_song_data(url: str, jwt: str) -> None:
    headers: dict[str, str] = {"Authorization": "Bearer " + jwt}
    response: requests.Response = requests.get(url, headers=headers)
    print(response.json())


def get_all_playlists(jwt_token) -> None:
    url: str = "https://api.music.apple.com/v1/me/library/playlists"
    music_user_token: str = TOKEN_PATH.read_text().strip()
    headers: dict[str, str] = {
        "Authorization": "Bearer " + jwt_token,
        "Music-User-Token": music_user_token,
    }
    response: requests.Response = requests.get(url, headers=headers)
    print(response.json())

    # Convert json to dict
    response_dict = response.json()

    playlists = print_playlists(response_dict)

    print(playlists)


def print_playlists(payload: dict) -> None:
    for item in payload.get("data", []):
        playlist_id = item.get("id")
        name = item.get("attributes", {}).get("name")

        if playlist_id and name:
            print(f"{name} ({playlist_id})")


def token_exists() -> bool:
    return TOKEN_PATH.exists() and TOKEN_PATH.read_text().strip() != ""


def main() -> None:
    key_id: str = cast(str, KEY_ID)
    team_id: str = cast(str, TEAM_ID)
    secret_key_file_path: str = cast(str, PRIVATE_KEY_PATH)
    # url: str = "https://api.music.apple.com/v1/catalog/us/songs/203709340"

    jwt: str = generate_jwt(secret_key_file_path, team_id, key_id)

    # get_song_data(url, jwt)
    if not token_exists():
        start_auth_flow()

    get_all_playlists(jwt)


if __name__ == "__main__":
    main()
