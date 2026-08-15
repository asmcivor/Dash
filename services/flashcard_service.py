from __future__ import annotations

#from curses import raw
#from curses import raw
from operator import add
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import urllib.request
import urllib.parse
from fastapi import Request
from urllib.parse import urlencode, quote
from functools import partial
import json
import logging
from venv import logger
from config import settings
import random
from constants import COOKIE_FLASHCARD_GAME_SESSION, COOKIE_FLASHCARD_OPTIONS
from services.cookie_helper import *

#logging setup
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("app.log", mode="a")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

class Operand(str, Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    RANDOM = "R"

# Cookies definitions
"""
DEFAULT_FLASHCARD_OPTIONS = {
    "operand": "+",
    "low_value": 0,
    "high_value": 20,
    "max_problems": 20,
    "timer": False,
    "timerval": 20,
    "stats": False
}

DEFAULT_FLASHCARD_GAME_SESSION = {
    "running" : False
}

"""
#OPTION_COOKIE_NAME = "flashcard_options"
#GAME_SESSION_COOKIE_NAME = "flashcard_game_session"



@dataclass
class Game:
    name: str = "Flashcard Game"
    description: str = "A simple flashcard game."
    user: str = "Player"
    operand: Operand = Operand.ADD
    low_value: int = 0
    high_value: int = 20
    max_problems: int = 20
    timer: bool = False
    timerval: int = 20
    stats: bool = False
    correct_count: int = 0
    wrong_count: int = 0
    problem_count: int = 0
    running: bool = False
    current_problem_index: int = 0
    problems: list[Problem] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Game":
        game = cls(
            running=data["running"],
            name=data["name"],
            description=data["description"],
            user=data["user"],
            low_value=data["low_value"],
            high_value=data["high_value"],
            operand=Operand(data["operand"]),
            max_problems=data["max_problems"],
            timer=data["timer"],
            timerval=data["timerval"],
            stats=data["stats"],
            correct_count=data["correct_count"],
            wrong_count=data["wrong_count"],
            problem_count=data["problem_count"],
            current_problem_index=data["current_problem_index"],
            problems=[Problem.from_dict(p) for p in data["problems"]],
        )
        return game

    def to_dict(self) -> dict:
        return {
            "running": self.running,
            "name": self.name,
            "description": self.description,
            "user": self.user,
            "low_value": self.low_value,
            "high_value": self.high_value,
            "operand": self.operand.value,
            "max_problems": self.max_problems,
            "timer": self.timer,
            "timerval": self.timerval,
            "stats": self.stats,
            "correct_count": self.correct_count,
            "wrong_count": self.wrong_count,
            "problem_count": self.problem_count,
            "current_problem_index": self.current_problem_index,
            "problems": [p.to_dict() for p in self.problems], 
        }
    
    def add_problem(self, problem: Problem) -> None:
        self.problems.append(problem)
        self.problem_count += 1
        self.current_problem_index = self.problem_count - 1

    def check_problem(self, answer: int, problem: Problem) -> bool:
        correct = False
        problem.user_answer = answer
        if problem.answer == answer:
            correct = True 
        problem.checked = True 
        problem.correct_answer = correct
        if correct:
            self.correct_count += 1
        else:
            self.wrong_count += 1
        return correct

@dataclass
class Problem:
    number1: int = 0
    number2: int = 0
    answer: int = 0
    checked: bool = False
    user_answer: int = 0
    correct_answer: bool = False
    operand: Operand = Operand.ADD

    def to_dict(self) -> dict:
        return {
            "number1": self.number1,
            "number2": self.number2,
            "answer": self.answer,
            "checked": self.checked,
            "user_answer": self.user_answer,
            "correct_answer": self.correct_answer,
            "operand": self.operand.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Problem":
        return cls(
            number1=data["number1"],
            number2=data["number2"],
            answer=data["answer"],
            checked=data["checked"],
            user_answer=data["user_answer"], 
            correct_answer=data["correct_answer"],
            operand=Operand(data["operand"]),
        )

class GameProcessor:
    def __init__(self, game: Game):
        self.game = game    
        self.logger = logging.getLogger()
        self.logger.debug(f"GameProcessor initialized for game: {self.game.name}")
        self.logger.debug(f"GameProcessor initialization complete.")

##class ProblemProcessor:
##    def __init__(self, problem: Problem):
##        self.problem = problem
##        self.logger = logging.getLogger()
##        self.logger.debug(f"ProblemProcessor initialized for problem: {self.problem}")
##        self.logger.debug(f"ProblemProcessor initialization complete.")


    def get_problem_values(self,operand : Operand) -> Problem:
        if operand == Operand.ADD:
            number1 = random.randint(self.game.low_value, self.game.high_value)
            number2 = random.randint(self.game.low_value, self.game.high_value)
            return Problem(number1=number1, number2=number2, answer=number1 + number2, operand=Operand.ADD)
        elif operand == Operand.SUBTRACT:
            number1 = random.randint(self.game.low_value, self.game.high_value)
            number2 = random.randint(self.game.low_value, number1)
            return Problem(number1=number1, number2=number2, answer=number1 - number2, operand=Operand.SUBTRACT)
        elif operand == Operand.MULTIPLY:
            number1 = random.randint(self.game.low_value, self.game.high_value)
            number2 = random.randint(self.game.low_value, self.game.high_value)
            return Problem(number1=number1, number2=number2, answer=number1 * number2, operand=Operand.MULTIPLY)
        elif operand == Operand.DIVIDE:
            number2 = random.randint(self.game.low_value, self.game.high_value)
            number2 = number2 if number2 != 0 else 1
            number1 = random.randint(number2, self.game.high_value)
            while number1 % number2 != 0:
                number1 = random.randint(number2, self.game.high_value)
            return Problem(number1=number1, number2=number2, answer=number1 // number2, operand=Operand.DIVIDE)
        else:  # Random case
            number1 = random.randint(self.game.low_value, self.game.high_value)
            number2 = random.randint(self.game.low_value, self.game.high_value)
            return Problem(number1=number1, number2=number2, answer=number1 + number2, operand=operand)



if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger()
    logger.debug("Flashcard service logging is set up.")