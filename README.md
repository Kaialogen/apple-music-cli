# apple-music-cli

apple-music-cli is a Python CLI tool that allows users to save and manage their Apple Music playlists efficiently. This application provides features to export playlists to CSV and JSON for backup or sharing.

> Disclaimer: This project uses the official Apple Music API but is not affiliated with or endorsed by Apple.

## Features

- Backup Apple Music playlists to local storage.
- Export playlists to CSV and JSON.
- Lightweight CLI for scripted backups

### Technical Details

- Uses Apple Music Developer Tokens (JWT) for API access
- Uses MusicKit JS in a local browser flow to obtain a Music User Token
- CLI communicates with the Apple Music API via HTTPS

### Future Features

- More file outputs.
- Playlist ID can either be the "p.b16GBvbHoRkkKo4" or the user-given name.

### Project Status

- This project is in active development.
- Breaking changes may occur before v1.0.0.

## Requirements

- Python 3.12+
- Windows/macOS/Linux (Needs to have a browser for MusicKit - cannot be run headless)

## Installation

1. Clone the repo:

```bash
git clone https://github.com/Kaialogen/apple-music-cli.git
cd apple-music-cli
```

2. Create and activate a virtual environment

```bash
uv pip install -e .
```

## Usage

On first run, the CLI will open a browser window to authenticate your Apple Music account.

Run the CLI entrypoint directly:

```python
uv run apple-music-cli --help
```

- Export a playlist to CSV:

```python
uv run apple-music-cli export --playlistID <PLAYLIST_ID> --format csv --out exports/playlist.csv
```

Common options:

```
- --playlistID <ID> Apple Music playlist identifier
- --out <path> Output file or directory
- --format <json|csv> Export format
```

You can also run the project using the Makefile targets on systems with make:

```
- make run # runs the CLI target (Makefile uses uv run python -m cli.main)
- make test # run pytest
- make lint # run ruff & mypy via configured targets
- make format # apply ruff formatting
```

On Windows without make, run the equivalent commands shown above directly.

## Authentication

Apple Music requires **two tokens**:

1. **Developer Token (JWT)**  
   Generated using your Apple Music private key (`.p8`).
   See Apple's docs for creating a developer key: https://developer.apple.com/documentation/applemusicapi

2. **Music User Token**  
   Obtained by authenticating the user via MusicKit JS in a browser.

Because of this, the CLI cannot run fully headless on first use.  
A browser window will open to authenticate the user and store a Music User Token locally for future CLI calls.

## Development & Testing

- Run unit tests:

```
python -m pytest -q -v --cov
```

- Lint & type-check:

```
ruff check .
mypy ./src
```

- Format:

```
ruff format .
```

Follow the existing code style (PEP 8, type hints where present).

## Contributing

If you want to contribute to this project, feel free to open an issue or a pull request. Contributions are welcome!

1. Fork the repo.
2. Create a branch: git checkout -b feat/short-description
3. Implement changes and add tests.
4. Run tests and linters locally.
5. Open a PR with a clear description and test coverage for the new behaviour.

Guidelines:

- Keep commits small and focused.
- Add/update tests for new behaviour.
- Prefer explicit typing and small utility functions.

## Reporting Issues

Open an issue with:

- Steps to reproduce
- Expected vs actual behaviour
- Python version and OS
- Relevant logs/traceback

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
