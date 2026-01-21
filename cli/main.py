import argparse
import logging
import os
from typing import cast

import requests
from dotenv import load_dotenv

from cli.auth import generate_jwt, start_auth_flow
from cli.config import TOKEN_PATH

load_dotenv()
logger: logging.Logger = logging.getLogger(__name__)


TEAM_ID: str | None = os.getenv("APPLE_MUSIC_TEAM_ID")
KEY_ID: str | None = os.getenv("APPLE_MUSIC_KEY_ID")
PRIVATE_KEY_PATH: str | None = os.getenv("APPLE_MUSIC_PRIVATE_KEY_PATH")

if not all([TEAM_ID, KEY_ID, PRIVATE_KEY_PATH]):
    raise RuntimeError(
        "Missing Apple Music credentials. "
        "Set APPLE_MUSIC_TEAM_ID, APPLE_MUSIC_KEY_ID, "
        "and APPLE_MUSIC_PRIVATE_KEY_PATH."
    )


def get_song_data(jwt: str) -> None:
    """
    Test function that should take a developer token and a known good URL and return data from the public catalogue.
    "Born in the U.S.A" by Bruce Springsteen should print to the terminal if the developer token is correct.

    :param jwt: Developer token string
    """
    url: str = "https://api.music.apple.com/v1/catalog/us/songs/203709340"
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
    logging.info("Got all playlists")

    # Convert json to dict
    response_dict = response.json()

    print_playlists(response_dict)


def get_playlist_by_id(jwt_token: str, playlist_id: str) -> None:
    """
    Docstring for get_playlist_by_id

    :param jwt_token: Developer token string
    """
    url: str = f"https://api.music.apple.com/v1/me/library/playlists/{playlist_id}"
    music_user_token: str = TOKEN_PATH.read_text().strip()
    headers: dict[str, str] = {
        "Authorization": "Bearer " + jwt_token,
        "Music-User-Token": music_user_token,
    }
    response: requests.Response = requests.get(url, headers=headers)
    logging.info("Found specific playlist")

    response_dict = response.json()
    print(response_dict)


def get_songs_in_playlist(jwt_token: str, playlist_id: str) -> None:
    """
    Gets songs from the specified playlist, limited to 100 songs internally.

    :param jwt_token: Developer token string
    :param playlist_id: id of the playlist to query
    """
    url: str = (
        f"https://api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks"
    )
    music_user_token: str = TOKEN_PATH.read_text().strip()
    headers: dict[str, str] = {
        "Authorization": "Bearer " + jwt_token,
        "Music-User-Token": music_user_token,
    }
    response: requests.Response = requests.get(url, headers=headers)
    logging.info("Found specific playlist")

    response_dict = response.json()
    print(response_dict)


def print_playlists(payload: dict) -> None:
    for item in payload.get("data", []):
        playlist_id = item.get("id")
        name = item.get("attributes", {}).get("name")

        if playlist_id and name:
            print(f"{name} ({playlist_id})")


def token_exists() -> bool:
    return TOKEN_PATH.exists() and TOKEN_PATH.read_text().strip() != ""


def parse_args():
    parser = argparse.ArgumentParser(
        prog="Apple Music CLI Playlist Saver",
        description="Python CLI tool to help users save Apple Music playlist data into various file formats.",
    )

    parser.add_argument(
        "COMMAND",
        help="Command to execute: Accepted commands - test, all-playlists, export, playlist",
        type=str,
    )

    parser.add_argument("--playlistID", type=str, help="id of playlist to backup")

    parser.add_argument("-f", "--format", type=str, help="output file format")

    parser.add_argument("-o", "--output", help="Output file.")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    key_id: str = cast(str, KEY_ID)
    team_id: str = cast(str, TEAM_ID)
    secret_key_file_path: str = cast(str, PRIVATE_KEY_PATH)

    jwt: str = generate_jwt(secret_key_file_path, team_id, key_id)

    if args.COMMAND == "test":
        get_song_data(jwt)
    elif args.COMMAND == "all-playlists":
        if not token_exists():
            start_auth_flow()
        get_all_playlists(jwt)
    elif args.COMMAND == "playlist" and args.playlistID:
        if not token_exists():
            start_auth_flow()
        get_playlist_by_id(jwt, args.playlistID)
    elif args.COMMAND == "export" and args.playlistID:
        if not token_exists():
            start_auth_flow()
        get_songs_in_playlist(jwt, args.playlistID)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
