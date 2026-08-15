import json
import urllib.parse
from fastapi import Request
from fastapi.responses import Response

# Cookies definitions
DEFAULT_FLASHCARD_OPTIONS = {
    "operand": "+",
    "low_value": 0,
    "high_value": 20,
    "max_problems": 20,
    "timer": False,
    "timerval": 20,
    "stats": True
}

DEFAULT_FLASHCARD_GAME_SESSION = {
    "running" : False,
    "name": "Flashcard Game",
    "description": "A simple flashcard game.",
    "user": "Player",
    "operand": "+",
    "low_value": 0,
    "high_value": 20,
    "max_problems": 20,
    "timer": False,
    "timerval": 20,
    "stats": False,
    "correct_count": 0,
    "wrong_count": 0,
    "problem_count": 0,
    "current_problem_index": 0,
    "problems": []
}

def set_json_cookie(response: Response, key: str, value: dict, max_age: int = 60*60*24*365, httponly: bool = True) -> None:
    """Serialize a dict to JSON and store it as a URL-encoded cookie."""
    response.set_cookie(
        key=key,
        value=urllib.parse.quote(json.dumps(value)),
        max_age=max_age,
        httponly=httponly,
        samesite="lax",
    )


def get_json_cookie(request: Request, key: str, default: dict = None) -> dict:
    """Read and deserialize a JSON cookie from the request."""
    raw = request.cookies.get(key)
    if raw is None:
        return default if default is not None else {}
    try:
        return json.loads(urllib.parse.unquote(raw))
    except (json.JSONDecodeError, ValueError):
        return default if default is not None else {}