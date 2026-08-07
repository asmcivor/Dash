from __future__ import annotations

from operator import add
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import urllib.request
import urllib.parse
from urllib.parse import urlencode, quote
from functools import partial
import json
import logging
from venv import logger
from config import settings
import random

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
    problem_count: int = 0
    current_problem_index: int = 0
    problems: list[Problem] = field(default_factory=list)  

@dataclass
class Problem:
    number1: int = 0
    number2: int = 0
    answer: int = 0
    operand: Operand = Operand.ADD
   

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

    def get_problem_values(self,gameproc: GameProcessor, Operand: Operand) -> Problem:
        if Operand == Operand.ADD:
            number1 = random.randint(gameproc.game.low_value, gameproc.game.high_value)
            number2 = random.randint(gameproc.game.low_value, gameproc.game.high_value)
            return Problem(number1=number1, number2=number2, answer=number1 + number2, operand=Operand.ADD)
        elif Operand == Operand.SUBTRACT:
            number1 = random.randint(gameproc.game.low_value, gameproc.game.high_value)
            number2 = random.randint(gameproc.game.low_value, number1)
            return Problem(number1=number1, number2=number2, answer=number1 - number2, operand=Operand.SUBTRACT)
        elif Operand == Operand.MULTIPLY:
            number1 = random.randint(gameproc.game.low_value, gameproc.game.high_value)
            number2 = random.randint(gameproc.game.low_value, gameproc.game.high_value)
            return Problem(number1=number1, number2=number2, answer=number1 * number2, operand=Operand.MULTIPLY)
        elif Operand == Operand.DIVIDE:
            number2 = random.randint(gameproc.game.low_value, gameproc.game.high_value)
            number2 = number2 if number2 != 0 else 1
            number1 = random.randint(number2, gameproc.game.high_value)
            while number1 % number2 != 0:
                number1 = random.randint(number2, gameproc.game.high_value)
            return Problem(number1=number1, number2=number2, answer=number1 // number2, operand=Operand.DIVIDE)
        else:
            number1 = random.randint(gameproc.game.low_value, gameproc.game.high_value)
            number2 = random.randint(gameproc.game.low_value, gameproc.game.high_value)
            return Problem(number1=number1, number2=number2, answer=number1 + number2, operand=Operand.ADD)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger()
    logger.debug("Flashcard service logging is set up.")