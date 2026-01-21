import os
from pathlib import Path

if os.name == "nt":
    appdata: str | None = os.getenv("APPDATA")
    base: Path = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
else:
    xdg = os.getenv("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"

TOKEN_PATH: Path = base / "apple_music_cli" / "music_user_token"
