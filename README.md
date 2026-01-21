# Apple Music CLI Playlist Saver

Apple Music Playlist Saver is a Python CLI tool that allows users to save and manage their Apple Music playlists efficiently. This application provides features to back up playlists, export them in various formats, and share them with friends.

> Disclaimer: Apple Music API is an unofficial application and not affiliated with Apple.

## Features

- Backup Apple Music playlists to local storage.
- Export playlists to CSV and JSON.
- Lightweight CLI for scripted backups

### Technical Details

## Requirements

- Python 3.12+
- Windows/MacOS/Linux (Needs to have browser for MusicKit - cannot be ran headless)

## CLI Usage

Run the CLI entrypoint directly:

```python
python -m cli.main --help
```

- Export a playlist to CSV:
  ```python
  python -m cli.main export --playlist-id <PLAYLIST_ID> --format csv --out exports/playlist.csv
  ```

You can also run the project using the Makefile targets on systems with make:

- make run # runs the CLI target (Makefile uses uv run python -m cli.main)
- make test # run pytest
- make lint # run ruff & mypy via configured targets
- make format # apply ruff formatting

On Windows without make, run the equivalent commands shown above directly.

## Installation

## Authentication

This project expects Apple Music developer credentials. You can use a .env file at the repo root (python-dotenv is included) or set environment variables directly.

- `APPLE_MUSIC_TEAM_ID`
- `APPLE_MUSIC_KEY_ID`
- `APPLE_MUSIC_PRIVATE_KEY_PATH` (path to your `.p8` private key)

Example .env:

```
APPLE_MUSIC_TEAM_ID=YOUR_TEAM_ID
APPLE_MUSIC_KEY_ID=YOUR_KEY_ID
APPLE_MUSIC_PRIVATE_KEY_PATH=C:\path\to\AuthKey_XXXXXX.p8
```

See Apple's docs for creating a developer key: https://developer.apple.com/documentation/applemusicapi

## Development & Testing

- Run unit tests:
  python -m pytest -q -v --cov

- Lint & type-check:
  ruff check .
  mypy ./cli

- Format:
  ruff format .

Follow the existing code style (PEP 8, type hints where present).

## Contributing

If you want to contribute to this project, feel free to open an issue or a pull request. Contributions are welcome!

1. Fork the repo.
2. Create a branch: git checkout -b feat/short-description
3. Implement changes and add tests.
4. Run tests and linters locally.
5. Open a PR with a clear description and test coverage for new behavior.

Guidelines:

- Keep commits small and focused.
- Add/update tests for new behavior.
- Prefer explicit typing and small utility functions.

## Reporting Issues

Open an issue with:

- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Relevant logs / traceback

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
