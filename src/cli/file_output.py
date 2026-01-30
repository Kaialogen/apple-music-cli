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


def write_songs_to_csv(
    payload: List[Dict], output_file: str = "output/output.csv"
) -> None:
    dictionary = payload[0]

    # Write to CSV file
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=dictionary.keys())
        writer.writeheader()
        writer.writerows(payload)
