from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from cli.config import TOKEN_PATH


class TokenPayload(BaseModel):
    token: str


app = FastAPI()


# Serve MusicKit Login page
@app.get("/login", response_class=HTMLResponse)
def login() -> str:
    return Path("server/templates/login.html").read_text()


# Receive and store Music User Token
@app.post("/callback")
def callback(payload: TokenPayload) -> dict[str, str]:
    TOKEN_PATH.write_text(payload.token)
    return {"status": "ok"}
