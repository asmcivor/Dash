from datetime import datetime
import logging
import json
import urllib.parse
from typing import Optional
from fastapi import APIRouter, Form, Request, Depends, Query, logger
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response

from dependencies import get_templates

from services.flashcard_service import Game, GameProcessor, Operand, Options, OptionError
from constants import COOKIE_RECENT_SEARCHES, MAX_RECENT_SEARCHES, COOKIE_FLASHCARD_GAME_SESSION, COOKIE_FLASHCARD_OPTIONS
from services.cookie_helper import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(tags=["partials"])

# Each route here returns an HTML fragment consumed by HTMX.
# HTMX swaps these fragments into the DOM without a full page reload.
# route for the address service


def build_game_from_cookies(request: Request) -> Game:
    gamesession = get_json_cookie(request, COOKIE_FLASHCARD_GAME_SESSION, DEFAULT_FLASHCARD_GAME_SESSION)
    logger.debug(f"Game session from cookies: {gamesession}")
    logger.debug(f"indexs are {gamesession.get('current_problem_index')} and problem count is {gamesession.get('problem_count')}")
    # get the options 
    options = get_json_cookie(request, COOKIE_FLASHCARD_OPTIONS, DEFAULT_FLASHCARD_OPTIONS)
    if gamesession["running"] is False:
        return Game(
            low_value=options["low_value"],
            high_value=options["high_value"],
            operand=Operand(options["operand"]),
            max_problems=options["max_problems"],
            timer=options["timer"],
            timerval=options["timerval"],
            stats=options["stats"],
        )
    else:
        game = Game.from_dict(gamesession)
        game.low_value = options["low_value"]
        game.high_value = options["high_value"]
        game.max_problems = options["max_problems"]
        game.timer = options["timer"]
        game.timerval = options["timerval"]
        game.stats = options["stats"]
        game.operand = Operand(options["operand"])
        logger.debug(f"Build_game_From_cookies: count = {game.problem_count} current_problem_index={game.current_problem_index} ")
        return game




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
            timerval=options["timerval"],
            max_problems=options["max_problems"],
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

@router.post("/flashcards-newgame")
async def flashcards_new(
    request: Request, templates: Jinja2Templates = Depends(get_templates)
):
    # This route handles the "New" action for the flashcard game, initializing a new game.
    options = get_json_cookie(request, COOKIE_FLASHCARD_OPTIONS, DEFAULT_FLASHCARD_OPTIONS)
    game = Game(
        low_value=options["low_value"],
        high_value=options["high_value"],
        operand=Operand(options["operand"]),
        timer=options["timer"],
        timerval=options["timerval"],
        max_problems=options["max_problems"],
        stats=options["stats"],
    )
    gameproc = GameProcessor(game)
    response = templates.TemplateResponse("partials/flashcards-content.html", {"request": request, "game": game})
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



    # advance the game to the next problem
    gameproc = GameProcessor(game)
    game.add_problem(gameproc.get_problem_values(game.operand))
    logger.debug(f"Game processor advanced to next problem: {game.problem_count} current index: {game.current_problem_index}")
    

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
    
    current_problem = game.problem if game.problem_count > 0 else None
    logger.debug(f"Current problem before answer: {game.problem}")
    if current_problem:
        correct = game.check_problem(answer, current_problem)
        if game.problem_count >= game.max_problems:
            game.gameover = True
        logger.debug(f"In Answer: problem_count={game.problem_count} current_problem_index={game.current_problem_index} correct={correct}")
    else:
        correct = None
    

    response = templates.TemplateResponse("partials/flashcards-content.html", {"request": request, "game": game})
    gamesession = game.to_dict()
    if game.gameover:
        gamesession["running"] = False
    else:
        gamesession["running"] = True
    set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, gamesession)
    return response 

@router.get("/flashcards-options")
async def flashcards_options(
    request: Request, templates: Jinja2Templates = Depends(get_templates)
):
    # This route handles the "Options" action for the flashcard game, returning the options content.
    options = get_json_cookie(request, COOKIE_FLASHCARD_OPTIONS, DEFAULT_FLASHCARD_OPTIONS)
    optionerror = OptionError()
    return templates.TemplateResponse("partials/flashcards-options.html", {"request": request, "options": options, "errors": optionerror})

@router.post("/flashcards-options")
async def flashcards_options_post(
    request: Request, templates: Jinja2Templates = Depends(get_templates)
):
    # This route handles the "Options" POST action for the flashcard game, updating the options.
    form = await request.form()
    try:
        operand = Operand(form.get("operand", "+"))
    except ValueError:
        logger.warning("Invalid operand value: %s, defaulting to ADD", form.get("operand"))
        operand = Operand.ADD
    options = Options(
        operand=Operand(form.get("operand", "+")),
        low_value=int(form.get("low_value", 0)),
        high_value=int(form.get("high_value", 20)),
        max_problems=int(form.get("max_problems", 20)),
        timer=form.get("timer") == "yes",
        timerval=int(form.get("timerval", 20)),
        stats=form.get("stats") == "yes"
    )
    optionerror = OptionError()
    # Validate options here, e.g., check low/high values, timer value, etc.
    if options.low_value > options.high_value:
        optionerror.low_high = "Low value must be less than high value."
    if options.timer and (options.timerval <= 0 or options.timerval > 60):
        optionerror.timer_error = "Timer value must be between 1 and 60 seconds."
    if optionerror.low_high or optionerror.timer_error:
        return templates.TemplateResponse("partials/flashcards-options.html", {"request": request, "options": options, "errors": optionerror})
    game = Game().from_dict(get_json_cookie(request, COOKIE_FLASHCARD_GAME_SESSION, {}))
    game.running = True
    game.low_value = options.low_value
    game.high_value = options.high_value
    #game.operand = Operand(options.operand)
    game.operand = options.operand
    game.max_problems = options.max_problems
    game.timer = options.timer
    game.timerval = options.timerval
    game.stats = options.stats
   
    response = templates.TemplateResponse("partials/flashcards-content.html", {"request": request, "game": game})
    set_json_cookie(response, COOKIE_FLASHCARD_OPTIONS, options.to_dict())
    gamesession = game.to_dict()
    gamesession["running"] = True
    set_json_cookie(response, COOKIE_FLASHCARD_GAME_SESSION, gamesession)
    
    return response