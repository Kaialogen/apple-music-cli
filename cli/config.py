import os
from pathlib import Path

if os.name == "NT":
    TOKEN_PATH = Path.home() / "%APPDATA%" / "apple_music_cli" / "music_user_token"
else:
    TOKEN_PATH: Path = Path.home() / ".config" / "apple_music_cli" / "music_user_token"
