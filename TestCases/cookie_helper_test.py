import json
import urllib.parse
import pytest
from unittest.mock import MagicMock
from fastapi.responses import HTMLResponse

from services.cookie_helper import *
from constants import COOKIE_FLASHCARD_GAME_SESSION

#local cookie for testing
DEFAULT_FLASHCARD_GAME_SESSION_TRUE = {"running": True}
FLASHCARD_GAME_SESSION_IN_PROGRESS = {
    "running" : True,
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
    "correct_count": 4,
    "wrong_count": 1,
    "problem_count": 5,
    "current_problem_index": 4,
    "problems": []
}


class TestSetJsonCookie:

    

    def test_cookie_name_is_set_correctly(self):
        response = MagicMock()
        set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION)
        _, kwargs = response.set_cookie.call_args
        assert kwargs["key"] == COOKIE_FLASHCARD_GAME_SESSION

    def test_cookie_value_is_json_serialized_with_in_progress(self):
        response = MagicMock()
        set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, FLASHCARD_GAME_SESSION_IN_PROGRESS)
        assert get_json_cookie(
            MagicMock(cookies={COOKIE_FLASHCARD_GAME_SESSION: urllib.parse.quote(json.dumps(FLASHCARD_GAME_SESSION_IN_PROGRESS))}),
              COOKIE_FLASHCARD_GAME_SESSION
            ) == FLASHCARD_GAME_SESSION_IN_PROGRESS

    def test_cookie_value_is_json_serialized(self):
        response = MagicMock()
        set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION)
        assert get_json_cookie(
            MagicMock(cookies={COOKIE_FLASHCARD_GAME_SESSION: urllib.parse.quote(json.dumps(DEFAULT_FLASHCARD_GAME_SESSION))}),
              COOKIE_FLASHCARD_GAME_SESSION
            ) == DEFAULT_FLASHCARD_GAME_SESSION

    def test_cookie_running_defaults_to_false(self):
        response = MagicMock()
        set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION)
        value = get_json_cookie(MagicMock(cookies={COOKIE_FLASHCARD_GAME_SESSION: urllib.parse.quote(json.dumps(DEFAULT_FLASHCARD_GAME_SESSION))}), COOKIE_FLASHCARD_GAME_SESSION)
        assert value["running"] is False
        assert value["stats"] is False
        assert value["max_problems"] == 20
        assert value["timerval"] == 20

    def test_cookie_running_is_true(self):
            response = MagicMock()
            set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, FLASHCARD_GAME_SESSION_IN_PROGRESS)
            value = get_json_cookie(MagicMock(cookies={COOKIE_FLASHCARD_GAME_SESSION: urllib.parse.quote(json.dumps(FLASHCARD_GAME_SESSION_IN_PROGRESS))}), 
                                    COOKIE_FLASHCARD_GAME_SESSION)
            assert value["running"] is True
            assert value["correct_count"] == 4
            assert value["wrong_count"] == 1
            assert value["problem_count"] == 5
            assert value["current_problem_index"] == 4
            
    def test_cookie_httponly_default_is_true(self):
        response = MagicMock()
        set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION)
        _, kwargs = response.set_cookie.call_args
        assert kwargs["httponly"] is True

    def test_cookie_httponly_can_be_overridden(self):
        response = MagicMock()
        set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION, httponly=False)
        _, kwargs = response.set_cookie.call_args
        assert kwargs["httponly"] is False

    def test_cookie_default_max_age_is_one_year(self):
        response = MagicMock()
        set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION)
        _, kwargs = response.set_cookie.call_args
        assert kwargs["max_age"] == 60 * 60 * 24 * 365

    def test_cookie_max_age_can_be_overridden(self):
        response = MagicMock()
        set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION, max_age=3600)
        _, kwargs = response.set_cookie.call_args
        assert kwargs["max_age"] == 3600

    def test_cookie_samesite_is_lax(self):
        response = MagicMock()
        set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION)
        _, kwargs = response.set_cookie.call_args
        assert kwargs["samesite"] == "lax"

    def test_cookie_value_is_url_encoded(self):
        response = MagicMock()
        set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION)
        _, kwargs = response.set_cookie.call_args
        # Raw value should be URL-encoded (no raw quotes or braces)
        assert '"' not in kwargs["value"]
        assert "{" not in kwargs["value"]