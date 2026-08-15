import urllib.parse
from typing import Optional
from fastapi import APIRouter, Form, Request, Depends, Query, logger
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response

from constants import COOKIE_FLASHCARD_GAME_SESSION, COOKIE_FLASHCARD_OPTIONS
from dependencies import get_templates

routerdev = APIRouter(tags=["partials"])

#dev tool - DELETE THIS LATER
@routerdev.get("/clear-cookies", response_class=HTMLResponse)
def clear_cookies(request: Request, response: Response):
    """Dev only — remove all game cookies for testing."""
    response = HTMLResponse("<p>Cookies cleared</p>")
    response.delete_cookie(COOKIE_FLASHCARD_GAME_SESSION)
    response.delete_cookie(COOKIE_FLASHCARD_OPTIONS)
    return response
