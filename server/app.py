from pathlib import Path
from typing import cast

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from cli.auth import generate_jwt
from cli.config import TOKEN_PATH
from cli.main import KEY_ID, PRIVATE_KEY_PATH, TEAM_ID


class TokenPayload(BaseModel):
    token: str


app = FastAPI()


# Serve MusicKit Login page
@app.get("/login", response_class=HTMLResponse)
def login() -> HTMLResponse:
    key_id: str = cast(str, KEY_ID)
    team_id: str = cast(str, TEAM_ID)
    secret_key_file_path: str = cast(str, PRIVATE_KEY_PATH)
    html: str = Path("server/templates/login.html").read_text()
    return HTMLResponse(
        html.replace(
            "{{ DEV_TOKEN }}", generate_jwt(secret_key_file_path, team_id, key_id)
        )
    )


# Receive and store Music User Token
@app.post("/callback")
def callback(payload: TokenPayload) -> dict[str, str]:
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(payload.token)
    return {"status": "ok"}
