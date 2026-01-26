import argparse
import logging
import os
from typing import Dict, List, cast

import requests
from dotenv import load_dotenv

from cli.auth import generate_jwt, start_auth_flow
from cli.config import TOKEN_PATH
from cli.file_output import write_songs_to_csv, write_songs_to_json

load_dotenv()
logger: logging.Logger = logging.getLogger(__name__)


TEAM_ID: str | None = os.getenv("APPLE_MUSIC_TEAM_ID")
KEY_ID: str | None = os.getenv("APPLE_MUSIC_KEY_ID")
PRIVATE_KEY_PATH: str | None = os.getenv("APPLE_MUSIC_PRIVATE_KEY_PATH")
BASE_URL = "https://api.music.apple.com"

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
    url: str = f"{BASE_URL}/v1/catalog/us/songs/203709340"
    headers: dict[str, str] = {"Authorization": "Bearer " + jwt}
    response: requests.Response = requests.get(url, headers=headers)
    print(response.json())


def get_all_playlists(jwt_token) -> None:
    url: str = f"{BASE_URL}/v1/me/library/playlists"
    music_user_token: str = TOKEN_PATH.read_text().strip()
    headers: dict[str, str] = {
        "Authorization": "Bearer " + jwt_token,
        "Music-User-Token": music_user_token,
    }
    try:
        response: requests.Response = requests.get(url, headers=headers)
        response.raise_for_status()
        logging.info("Got all playlists")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(
                "Unauthorized: A response indicating an incorrect Authorization header."
            )
        elif e.response.status_code == 403:
            print(
                "Forbidden: A response indicating invalid or insufficient authentication."
            )
        elif e.response.status_code == 429:
            print("Too Many Requests. Rate limited by Apple servers")
        elif e.response.status_code == 500:
            print(
                "Internal Server Error: A response indicating an error occurred on the server."
            )
        else:
            print(f"HTTP error occurred: {e}")
        return None

    # Convert json to dict
    response_dict = response.json()

    all_playlists = dict()

    for data in response_dict.values():
        print(data)


def print_playlists(payload: dict) -> list:
    """Return a list of [name, id] pairs for playlists in the payload."""
    return [
        [item.get("attributes", {}).get("name"), item.get("id")]
        for item in payload.get("data", [])
        if item.get("id") and item.get("attributes", {}).get("name")
    ]


def get_playlist_by_id(jwt_token: str, playlist_id: str) -> None:
    """
    Docstring for get_playlist_by_id

    :param jwt_token: Developer token string
    """
    url: str = f"{BASE_URL}/v1/me/library/playlists/{playlist_id}"
    music_user_token: str = TOKEN_PATH.read_text().strip()
    headers: dict[str, str] = {
        "Authorization": "Bearer " + jwt_token,
        "Music-User-Token": music_user_token,
    }
    response: requests.Response = requests.get(url, headers=headers)
    logging.info("Found specific playlist")

    response_dict = response.json()
    print(response_dict)


def get_songs_in_playlist(jwt_token: str, playlist_id: str) -> Dict:
    """
    Gets songs from the specified playlist, limited to 100 songs internally.

    :param jwt_token: Developer token string
    :param playlist_id: Apple Music library playlist ID
    :return: Full response dict with aggregated data
    """
    url: str | None = f"{BASE_URL}/v1/me/library/playlists/{playlist_id}/tracks"
    music_user_token: str = TOKEN_PATH.read_text().strip()
    headers: dict[str, str] = {
        "Authorization": f"Bearer {jwt_token}",
        "Music-User-Token": music_user_token,
    }

    all_tracks: List[dict] = []
    while url:
        response: requests.Response = requests.get(url, headers=headers)
        response.raise_for_status()

        payload = response.json()
        tracks = payload.get("data", [])
        all_tracks.extend(tracks)

        logging.info("Fetched %d tracks", len(tracks))

        next_path = payload.get("next")
        if next_path:
            url = BASE_URL + next_path
        else:
            url = None

    return {"data": all_tracks, "total": len(all_tracks)}


def token_exists() -> bool:
    return TOKEN_PATH.exists() and TOKEN_PATH.read_text().strip() != ""


def parse_args():
    parser = argparse.ArgumentParser(
        prog="apple-music-cli",
        description="Python CLI tool to help users save Apple Music playlist data into various file formats.",
    )

    parser.add_argument(
        "COMMAND",
        help="Command to execute: Accepted commands - test, all-playlists, export, playlist",
        type=str,
    )

    parser.add_argument("--playlistID", type=str, help="id of playlist to backup")

    parser.add_argument(
        "-f", "--format", type=str, help="output file format", default="json"
    )

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
        output = get_songs_in_playlist(jwt, args.playlistID)
        if args.format == "json":
            write_songs_to_json(output, args.output)
        elif args.format == "csv":
            write_songs_to_csv(output, args.output)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
