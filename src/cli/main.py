import argparse
import logging
import os
from datetime import datetime
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


def get_song_data(jwt_token: str) -> None:
    """
    Test function that should take a developer token and a known good URL and return data from the public catalogue.
    "Born in the U.S.A" by Bruce Springsteen should print to the terminal if the developer token is correct.

    :param jwt_token: A developer JWT used as the Bearer token in the Authorization header.
    """
    url: str = f"{BASE_URL}/v1/catalog/us/songs/203709340"
    headers: Dict[str, str] = {"Authorization": "Bearer " + jwt_token}

    try:
        response: requests.Response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info("Got song")
    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        if status == 401:
            print("Unauthorized: Incorrect Authorization header or token expired.")
        elif status == 403:
            print("Forbidden: Invalid or insufficient authentication.")
        elif status == 429:
            print("Too Many Requests: Rate limited by Apple servers.")
        elif status == 500:
            print("Internal Server Error: An error occurred on the server.")
        else:
            print(f"HTTP error occurred: {e}")
        logging.exception("HTTP error fetching playlists")
        return None
    except requests.exceptions.RequestException as e:
        logging.exception("Network error while fetching playlists")
        print(f"Network error while fetching playlists: {e}")
        return None

    try:
        response_dict = response.json()
    except ValueError:
        logging.exception("Failed to parse JSON response")
        print("Invalid JSON received from Apple Music API.")
        return None

    print(response_dict)


def get_all_playlists(jwt_token: str) -> List[Dict[str, str]] | None:
    """
    Retrieve all Apple Music library playlists for the authenticated user.

    Sends a GET request to the Apple Music API endpoint for the current user's library playlists,
    using the provided developer JWT for the Authorization header and reading the Music-User-Token
    from TOKEN_PATH.

    :param jwt_token: A developer JWT used as the Bearer token in the Authorization header.
    :return: On success, returns a list of playlist dictionaries with the following keys:
        - "name": str | None, playlist name
        - "id": str | None, playlist identifier
        - "dateAdded": str | None, date the playlist was added formatted as "DD-MM-YYYY"
    Returns None if an error occurs; prints a short message describing common HTTP/errors
    before returning None.
    """
    url: str = f"{BASE_URL}/v1/me/library/playlists"

    try:
        music_user_token: str = TOKEN_PATH.read_text().strip()
        if not music_user_token:
            logging.error("Music user token is empty.")
            print("Music user token is missing. Please authenticate.")
            return None
    except Exception as e:
        logging.exception(
            f"Failed to read Music-User-Token from TOKEN_PATH. Error: {e}"
        )
        print("Unable to read Music-User-Token. Make sure you have authenticated.")
        return None

    headers: Dict[str, str] = {
        "Authorization": "Bearer " + jwt_token,
        "Music-User-Token": music_user_token,
    }

    try:
        response: requests.Response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info("Got all playlists")
    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        if status == 401:
            print("Unauthorized: Incorrect Authorization header or token expired.")
        elif status == 403:
            print("Forbidden: Invalid or insufficient authentication.")
        elif status == 429:
            print("Too Many Requests: Rate limited by Apple servers.")
        elif status == 500:
            print("Internal Server Error: An error occurred on the server.")
        else:
            print(f"HTTP error occurred: {e}")
        logging.exception("HTTP error fetching playlists")
        return None
    except requests.exceptions.RequestException as e:
        logging.exception("Network error while fetching playlists")
        print(f"Network error while fetching playlists: {e}")
        return None

    try:
        response_dict = response.json()
    except ValueError:
        logging.exception("Failed to parse JSON response")
        print("Invalid JSON received from Apple Music API.")
        return None

    playlists = response_dict.get("data", [])
    if not isinstance(playlists, list):
        logging.error("Unexpected playlists format in response")
        print("Unexpected response format from Apple Music API.")
        return None

    output: List[Dict[str, str]] = []
    for item in playlists:
        if not isinstance(item, dict):
            continue
        attributes = item.get("attributes") or {}
        name = attributes.get("name") if isinstance(attributes, dict) else None
        pid = item.get("id")
        date_added = (
            attributes.get("dateAdded") if isinstance(attributes, dict) else None
        )

        date_str: str | None = None
        if date_added:
            try:
                dt = datetime.fromisoformat(date_added)
                date_str = dt.strftime("%d-%m-%Y")
            except Exception:
                logging.warning(
                    "Invalid dateAdded format for playlist id %s: %s", pid, date_added
                )
                date_str = None

        playlist = {
            "name": name,
            "id": pid,
            "dateAdded": date_str,
        }
        output.append(playlist)

    return output


def get_playlist_by_id(jwt_token: str, playlist_id: str) -> List[Dict[str, str]] | None:
    """
    Retrieve a specified playlist for the authenticated user.

    :param jwt_token: A developer JWT used as the Bearer token in the Authorization header.
    """
    url: str = f"{BASE_URL}/v1/me/library/playlists/{playlist_id}"

    try:
        music_user_token: str = TOKEN_PATH.read_text().strip()
        if not music_user_token:
            logging.error("Music user token is empty.")
            print("Music user token is missing. Please authenticate.")
            return None
    except Exception as e:
        logging.exception(
            f"Failed to read Music-User-Token from TOKEN_PATH. Error: {e}"
        )
        print("Unable to read Music-User-Token. Make sure you have authenticated.")
        return None

    headers: Dict[str, str] = {
        "Authorization": "Bearer " + jwt_token,
        "Music-User-Token": music_user_token,
    }

    try:
        response: requests.Response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info("Found playlist")
    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        if status == 401:
            print("Unauthorized: Incorrect Authorization header or token expired.")
        elif status == 403:
            print("Forbidden: Invalid or insufficient authentication.")
        elif status == 429:
            print("Too Many Requests: Rate limited by Apple servers.")
        elif status == 500:
            print("Internal Server Error: An error occurred on the server.")
        else:
            print(f"HTTP error occurred: {e}")
        logging.exception("HTTP error fetching playlists")
        return None
    except requests.exceptions.RequestException as e:
        logging.exception("Network error while fetching playlists")
        print(f"Network error while fetching playlists: {e}")
        return None

    try:
        response_dict = response.json()
    except ValueError:
        logging.exception("Failed to parse JSON response")
        print("Invalid JSON received from Apple Music API.")
        return None

    playlists = response_dict.get("data", [])
    if not isinstance(playlists, list):
        logging.error("Unexpected playlists format in response")
        print("Unexpected response format from Apple Music API.")
        return None

    output: List[Dict[str, str]] = []
    for item in playlists:
        if not isinstance(item, dict):
            continue
        attributes = item.get("attributes") or {}
        name = attributes.get("name") if isinstance(attributes, dict) else None
        pid = item.get("id")
        date_added = (
            attributes.get("dateAdded") if isinstance(attributes, dict) else None
        )

        date_str: str | None = None
        if date_added:
            try:
                dt = datetime.fromisoformat(date_added)
                date_str = dt.strftime("%d-%m-%Y")
            except Exception:
                logging.warning(
                    "Invalid dateAdded format for playlist id %s: %s", pid, date_added
                )
                date_str = None

        playlist = {
            "name": name,
            "id": pid,
            "dateAdded": date_str,
        }
        output.append(playlist)
    return output


def get_songs_in_playlist(jwt_token: str, playlist_id: str) -> List[Dict]:
    """
    Gets songs from the specified playlist, limited to 100 songs internally.

    :param jwt_token: A developer JWT used as the Bearer token in the Authorization header.
    :param playlist_id: Apple Music library playlist ID
    :return: Full response dict with aggregated data
    """
    url: str = f"{BASE_URL}/v1/me/library/playlists/{playlist_id}/tracks"

    try:
        music_user_token: str = TOKEN_PATH.read_text().strip()
        if not music_user_token:
            logging.error("Music user token is empty.")
            print("Music user token is missing. Please authenticate.")
            return None
    except Exception as e:
        logging.exception(
            f"Failed to read Music-User-Token from TOKEN_PATH. Error: {e}"
        )
        print("Unable to read Music-User-Token. Make sure you have authenticated.")
        return None

    headers: Dict[str, str] = {
        "Authorization": "Bearer " + jwt_token,
        "Music-User-Token": music_user_token,
    }

    all_tracks: List[Dict] = []
    while url:
        try:
            response: requests.Response = requests.get(url, headers=headers)
            response.raise_for_status()
            logging.info("Found playlist")
        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            if status == 401:
                print("Unauthorized: Incorrect Authorization header or token expired.")
            elif status == 403:
                print("Forbidden: Invalid or insufficient authentication.")
            elif status == 429:
                print("Too Many Requests: Rate limited by Apple servers.")
            elif status == 500:
                print("Internal Server Error: An error occurred on the server.")
            else:
                print(f"HTTP error occurred: {e}")
            logging.exception("HTTP error fetching songs")
            return None
        except requests.exceptions.RequestException as e:
            logging.exception("Network error while fetching songs")
            print(f"Network error while fetching songs: {e}")
            return None

        try:
            payload = response.json()
        except ValueError:
            logging.exception("Failed to parse JSON response")
            print("Invalid JSON received from Apple Music API.")
            return None

        tracks = payload.get("data", [])

        all_tracks.extend(tracks)

        logging.info("Fetched %d tracks", len(tracks))

        next_path = payload.get("next")
        if next_path:
            url = BASE_URL + next_path
        else:
            url = None

    payload = {"data": all_tracks, "total": len(all_tracks)}
    songs: List[Dict] = []

    for item in payload.get("data", []):
        attributes = item.get("attributes", {})
        if not attributes:
            continue

        song = {
            "name": attributes.get("name"),
            "artistName": attributes.get("artistName"),
            "albumName": attributes.get("albumName"),
            "genreNames": attributes.get("genreNames", []),
            "releaseDate": attributes.get("releaseDate"),
        }

        songs.append(song)

    return songs


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

    def _write_output(data):
        if data is None:
            print("No data to write.")
            return
        fmt = (args.format or "json").lower()
        if fmt == "json":
            write_songs_to_json(data, args.output)
        elif fmt == "csv":
            write_songs_to_csv(data, args.output)
        else:
            print(f"Unknown format: {args.format}")

    cmd = (args.COMMAND or "").lower()

    if cmd == "test":
        get_song_data(jwt)
        return

    if cmd == "all-playlists":
        if not token_exists():
            start_auth_flow()
        output = get_all_playlists(jwt)
        _write_output(output)
        return

    if cmd in {"playlist", "export"}:
        if not args.playlistID:
            print("playlistID is required for this command.")
            return
        if not token_exists():
            start_auth_flow()
        if cmd == "playlist":
            output = get_playlist_by_id(jwt, args.playlistID)
        else:
            output = get_songs_in_playlist(jwt, args.playlistID)
        _write_output(output)
        return

    print(f"Unknown command: {args.COMMAND}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
