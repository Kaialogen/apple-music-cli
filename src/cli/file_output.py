import csv
import json
from pathlib import Path
from typing import Dict, List


def write_songs_to_json(
    payload: List[Dict], output_file: str = "output/output.json"
) -> None:
    # Write to JSON file
    Path(output_file).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_songs_to_csv(payload: dict, output_file: str = "output/output.csv") -> None:
    songs: list[dict] = []

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

    # Define the field names
    field_names: list[str] = [
        "name",
        "artistName",
        "albumName",
        "genreNames",
        "releaseDate",
    ]

    # Write to CSV file
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(songs)
