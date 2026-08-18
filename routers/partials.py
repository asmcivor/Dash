from datetime import datetime
import logging
import json
import urllib.parse
from typing import Optional
from fastapi import APIRouter, Form, Request, Depends, Query, logger
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response

from dependencies import get_templates
from services.data_service import DataService
#from services.time_service import TimeService
from services.address_service import AddressProcessor, Address
from services.flashcard_service import Game, GameProcessor, Operand
from services.weather_service import WeatherProcessor, WeatherReading, TempUnit, SpeedUnit, weather_code
from constants import COOKIE_RECENT_SEARCHES, MAX_RECENT_SEARCHES, COOKIE_FLASHCARD_GAME_SESSION, COOKIE_FLASHCARD_OPTIONS
from services.cookie_helper import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(tags=["partials"])

# Each route here returns an HTML fragment consumed by HTMX.
# HTMX swaps these fragments into the DOM without a full page reload.
# route for the address service

#TEMP GLOBAL NUMBER NEXT PROBLEM COUNT
NEXTCOUNT: int = 0
def build_game_from_cookies(request: Request) -> Game:
    gamesession = get_json_cookie(request, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION)
    logger.debug(f"Game session from cookies: {gamesession}")
    logger.debug(f"indexs are {gamesession.get('current_problem_index')} and problem count is {gamesession.get('problem_count')}")
    if gamesession["running"] is False:
        options = get_json_cookie(request, COOKIE_FLASHCARD_OPTIONS, DEFAULT_FLASHCARD_OPTIONS)
        return Game(
            low_value=options["low_value"],
            high_value=options["high_value"],
            operand=Operand(options["operand"]),
            timer=options["timer"],
            stats=options["stats"],
        )
    else:
        game = Game.from_dict(gamesession) 
        logger.debug(f"Build_game_From_cookies: count = {game.problem_count} current_problem_index={game.current_problem_index} length of problem is {len(game.problems)}")
        return game

def get_recent_searches(request: Request) -> list[str]:
    raw = request.cookies.get(COOKIE_RECENT_SEARCHES, "[]")
    try:
        return json.loads(urllib.parse.unquote(raw))
    except Exception:
        return []

def build_updated_searches(current: list[str], new_entry: str) -> list[str]:
    trimmed = new_entry.strip()
    updated = [s for s in current if s.lower() != trimmed.lower()]
    updated.insert(0, trimmed)
    return updated[:MAX_RECENT_SEARCHES]


# Route for the new flashcard interface
@router.get("/flashcards-content")
async def flashcards_content(
    request: Request, templates: Jinja2Templates = Depends(get_templates)):

    gamesession = get_json_cookie(request, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION)

    if gamesession["running"] is False:
        options = get_json_cookie(request, COOKIE_FLASHCARD_OPTIONS, DEFAULT_FLASHCARD_OPTIONS)
        game = Game(
            low_value=options["low_value"],
            high_value=options["high_value"],
            operand=Operand(options["operand"]),
            timer=options["timer"],
            stats=options["stats"],
        )
    else:
        game = Game.from_dict(gamesession)

    gameproc = GameProcessor(game)
    logger.debug(f"Game processor initialized with game: {game}")
    response = templates.TemplateResponse(
        "partials/flashcards-content.html",
        {"request": request, "game": game},
    )
    gamesession = game.to_dict()
    gamesession["running"] = True
    set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, gamesession)
    return response

@router.post("/flashcards-next")
async def flashcards_next(
    request: Request, templates: Jinja2Templates = Depends(get_templates)
):
    # This route handles the "Next" action for the flashcard game, returning the updated flashcard content.
    # check if a game is running and if so get the current game state from the cookie, otherwise initialize a new game
    game = build_game_from_cookies(request)
    global NEXTCOUNT
    NEXTCOUNT += 1
    logger.debug(f"In Next: NEXTCOUNT={NEXTCOUNT}")


    # advance the game to the next problem
    gameproc = GameProcessor(game)
    game.add_problem(gameproc.get_problem_values(game.operand))
    logger.debug(f"Game processor advanced to next problem: {game.problem_count} current index: {game.current_problem_index}")
    logger.debug(f"Current problem: {game.problems[game.current_problem_index] if game.problem_count > 0 else None}")
    logger.debug(f"In Next problem_count={game.problem_count} current_problem_index={game.current_problem_index}")

    response = templates.TemplateResponse("partials/flashcards-content.html", {"request": request, "game": game})
    gamesession = game.to_dict()
    gamesession["running"] = True
    set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, gamesession)
    return response

@router.post("/flashcards-answer")
async def flashcards_answer(
    request: Request, templates: Jinja2Templates = Depends(get_templates)
):
    # This route handles the "Answer" action for the flashcard game, returning the updated flashcard content.
    game = build_game_from_cookies(request)
    form = await request.form()
    answer = int(form.get("answer", 0))
    logger.debug(f"Form data received: {form}")
    logger.debug(f"game info: {game}")
    logger.debug(f"Current problem before answer: {game.problems[game.current_problem_index] if game.problem_count > 0 else None}")
    current_problem = game.problems[game.current_problem_index] if game.problem_count > 0 else None
    logger.debug(f"Current problem before answer: {current_problem}")
    if current_problem:
        correct = game.check_problem(answer, current_problem)
        logger.debug(f"In Answer: problem_count={game.problem_count} current_problem_index={game.current_problem_index} correct={correct}")
    else:
        correct = None
    

    response = templates.TemplateResponse("partials/flashcards-content.html", {"request": request, "game": game})
    gamesession = game.to_dict()
    gamesession["running"] = True
    for problem in game.problems:
        logger.debug(f"Game problem_count={game.problem_count} current_problem_index={game.current_problem_index} Problem:{problem.number1} ,{problem.number2}, {problem.answer} user_answer={problem.user_answer}")
    set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, gamesession)
    return response 

#load the weather from a cookie on load
@router.get("/weather-load", response_class=HTMLResponse)
async def weather_load(
    request: Request,
    city_state: Optional[str] = Query(default=None),
    timezone: Optional[str] = Query(default="UTC"),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Auto-loads weather on page ready using cookie value."""
    if city_state is None:
        return HTMLResponse(content="")  # nothing to load yet
    # get the 0th position from the get_recent_searches
    if city_state is None:
        recent_searches = get_recent_searches(request)
        if recent_searches:
            city_state = recent_searches[0]
    return await _get_weather_response(request, city_state, timezone, templates)


@router.post("/getWeatherForAddress", response_class=HTMLResponse)
async def get_weather_for_address(
    request: Request,
    city_state: Optional[str] = Form(None),
    timezone: Optional[str] = Form("UTC"),
    templates: Jinja2Templates = Depends(get_templates),
):
    """HTMX target: hx-post="/getWeatherForAddress" """
    recent  = get_recent_searches(request)
    updated = build_updated_searches(recent, city_state)

    response = await _get_weather_response(request, city_state, timezone, templates)
    response.set_cookie(
        key      = COOKIE_RECENT_SEARCHES,
        value    = urllib.parse.quote(json.dumps(updated)),
        max_age  = 60 * 60 * 24 * 365,  # 1 year
        httponly = False,   # False so JS can read it for the dropdown
        samesite = "lax",
    )
    #response.set_cookie(key="last_weather_location", value=city_state, max_age=60*60*24*30, httponly=True, samesite="lax")
    return response

async def _get_weather_response(
    request: Request,
    city_state: str,
    timezone: str,
    templates: Jinja2Templates,
) -> HTMLResponse:
    """Shared logic for fetching and rendering weather data."""
    logger.info("RF Processing weather request for address.")
    logger.debug(f"Received form data: city_state={city_state}, timezone={timezone}")
    aproc = AddressProcessor()
    wproc = WeatherProcessor()

    addressstring = Address.parse_address_s(city_state)
    if addressstring is None:
        logger.error("Failed to parse address information.")
        return templates.TemplateResponse(
            "partials/weatherError.html",
            {"request": request, "error_message": f"Unable to retrieve weather information for the provided address: {city_state}."},
        )

    addressresponse = aproc.get_addressByPostalCode(Address(street="", city=addressstring.city, state=addressstring.state, zip_code=addressstring.zip_code, country=""))
    if addressresponse is None:
        logger.error("Failed to retrieve address information.")
        return templates.TemplateResponse(
            "partials/weatherError.html",
            {"request": request, "error_message": f"Unable to retrieve weather information for the provided address: {city_state}."},
        )

    weather_address = Address.from_api_response(addressresponse[0])
    try:
        logger.debug(f"Fetching weather for address: {weather_address}, timezone: {timezone}")
        weather_response = wproc.get_current(weather_address, timezone)
    except RuntimeError as e:
        logger.error("Failed to retrieve weather information.")
        return templates.TemplateResponse(
            "partials/weatherError.html",
            {"request": request, "error_message": str(e)},
        )

    current_weather = WeatherReading.from_api_response(weather_response[0], weather_address)
    icon = WeatherProcessor().getweatherdescription(current_weather.weather_snapshot, weather_code.ICON)

    return templates.TemplateResponse(
        "partials/weather.html",
        {"request": request, "current_weather": current_weather, "icon": icon},
    )

#route for the time service
@router.get("/current_time", response_class=HTMLResponse)
async def current_time_partial(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-get="/current_time" hx-trigger="load" hx-target="#time-container"
    Returns the current time fragment.
    """

    #service = TimeService()
    #time_data = await service.get_current_time()
    time_data = datetime.now()

    return templates.TemplateResponse(
        "partials/current_time.html",
        {"request": request, "time_data": time_data.strftime("%Y-%m-%d")},
    )

#route for the reports page.
@router.get("/reports", response_class=HTMLResponse)
async def reports_partial(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-get="/partials/reports" hx-target="#reports-container"
    Returns the reports fragment.
    """
    service = DataService()
    reports = await service.get_reports()

    return templates.TemplateResponse(
        "partials/reports.html",
        {"request": request, "reports": reports},
    )

@router.get("/stats", response_class=HTMLResponse)
async def stats_partial(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-get="/partials/stats" hx-target="#stats-container"
    Returns the stats cards fragment.
    """
    service = DataService()
    stats = await service.get_stats()

    return templates.TemplateResponse(
        "partials/stats_card.html",
        {"request": request, "stats": stats},
    )


@router.get("/table", response_class=HTMLResponse)
async def table_partial(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100),
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-get="/partials/table?page=1" hx-target="#data-table"
    Supports pagination via query params — HTMX passes these automatically.
    """
    service = DataService()
    rows, total = await service.get_table_data(page=page, limit=limit)

    return templates.TemplateResponse(
        "partials/data_table.html",
        {
            "request": request,
            "rows": rows,
            "page": page,
            "total": total,
            "limit": limit,
        },
    )


@router.post("/item", response_class=HTMLResponse)
async def create_item_partial(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    """
    HTMX target: hx-post="/partials/item" hx-target="#items-list" hx-swap="afterbegin"
    Creates an item and returns just the new row HTML to prepend.
    """
    form = await request.form()
    service = DataService()
    new_item = await service.create_item(dict(form))

    return templates.TemplateResponse(
        "partials/item_row.html",
        {"request": request, "item": new_item},
    )
