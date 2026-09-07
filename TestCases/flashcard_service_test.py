import json
import urllib.parse
from fastapi import Request
from fastapi.responses import Response
import pytest 
import logging
from unittest.mock import MagicMock
from services.flashcard_service import Game, GameProcessor, Options, Problem, Operand
from constants import COOKIE_FLASHCARD_GAME_SESSION, COOKIE_FLASHCARD_OPTIONS
from services.cookie_helper import *

DEFAULT_FLASHCARD_GAME_SESSION = {"running": False}

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

class TestGameplay:
    def test_setup(self):
        game = Game()
        assert game.name == "Flashcard Game"
        assert game.description == "A simple flashcard game."
        assert game.user == "Player"
        assert game.max_problems == 20
        assert game.operand == Operand.ADD
        assert game.low_value == 0
        assert game.high_value == 20
        assert game.timer == False
        assert game.timerval == 20
        assert game.stats == False
        assert game.problem_count == 0


    def test_optional_parameters(self):
        game = Game(user="Alan", max_problems=20)
        assert game.user == "Alan"
        assert game.max_problems == 20
        assert game.problem_count == 0

    def test_no_cookie_values(self):
        game = Game()
        gameproc = GameProcessor(game)
        gamesession = get_json_cookie(
            MagicMock(cookies={COOKIE_FLASHCARD_GAME_SESSION: urllib.parse.quote(json.dumps(FLASHCARD_GAME_SESSION_IN_PROGRESS))}),
            COOKIE_FLASHCARD_GAME_SESSION)
        assert gamesession == FLASHCARD_GAME_SESSION_IN_PROGRESS
        assert gamesession["running"] is True

    def test_no_cookie_value_use_default(self):
            game = Game()
            gameproc = GameProcessor(game)
            gamesession = get_json_cookie(
                MagicMock(cookies={COOKIE_FLASHCARD_GAME_SESSION: urllib.parse.quote(json.dumps(DEFAULT_FLASHCARD_GAME_SESSION))}),
                COOKIE_FLASHCARD_GAME_SESSION,
                DEFAULT_FLASHCARD_GAME_SESSION)
            assert gamesession == DEFAULT_FLASHCARD_GAME_SESSION
            assert gamesession["running"] is False

    def test_cookie_management_save(self):
        response = MagicMock()
        requestsession = MagicMock(cookies={COOKIE_FLASHCARD_GAME_SESSION: urllib.parse.quote(json.dumps(DEFAULT_FLASHCARD_GAME_SESSION))})
        requestoptions = MagicMock(cookies={COOKIE_FLASHCARD_OPTIONS: urllib.parse.quote(json.dumps(DEFAULT_FLASHCARD_OPTIONS))})  
        gamesession = get_json_cookie(request=requestsession, key=COOKIE_FLASHCARD_GAME_SESSION, default=DEFAULT_FLASHCARD_GAME_SESSION)
        # Pretend the game is running and save the session to the response cookie
        assert gamesession["running"] is False
        # get the options and then create a game
        options = get_json_cookie(request=requestoptions,key=COOKIE_FLASHCARD_OPTIONS, default=DEFAULT_FLASHCARD_OPTIONS)
        game = Game(
           operand=Operand(options["operand"]),
           low_value=options["low_value"],
           high_value=options["high_value"],
           max_problems=options["max_problems"],
           timer=options["timer"],
           timerval=options["timerval"],
           stats=options["stats"]
        )
       #setup the game processor
        gameproc = GameProcessor(game)
        game.running = True
        game.current_problem_index = 5
        #save the game state
        gamesessionNew = game.to_dict()
        set_json_cookie(response=response, key=COOKIE_FLASHCARD_GAME_SESSION, value=gamesessionNew)
        
    
       # Verify that the game session was correctly saved and can be retrieved from the cookie
        reqeustsession2 = MagicMock(cookies={COOKIE_FLASHCARD_GAME_SESSION: urllib.parse.quote(json.dumps(gamesessionNew))})
        retrieved_game = get_json_cookie(request=reqeustsession2, key=COOKIE_FLASHCARD_GAME_SESSION, default=DEFAULT_FLASHCARD_GAME_SESSION)
        assert retrieved_game["current_problem_index"] == 5
        assert retrieved_game["running"] is True
    def test_gameover_start(self):
        response = MagicMock()
        requestsession = MagicMock(cookies={COOKIE_FLASHCARD_GAME_SESSION: urllib.parse.quote(json.dumps(DEFAULT_FLASHCARD_GAME_SESSION))})
        requestoptions = MagicMock(cookies={COOKIE_FLASHCARD_OPTIONS: urllib.parse.quote(json.dumps(DEFAULT_FLASHCARD_OPTIONS))})  
        gamesession = get_json_cookie(request=requestsession, key=COOKIE_FLASHCARD_GAME_SESSION, default=DEFAULT_FLASHCARD_GAME_SESSION)
                # Pretend the game is running and save the session to the response cookie
        assert gamesession["running"] is False
                # get the options and then create a game
        options = get_json_cookie(request=requestoptions,key=COOKIE_FLASHCARD_OPTIONS, default=DEFAULT_FLASHCARD_OPTIONS)
        game = Game(
                   operand=Operand(options["operand"]),
                   low_value=options["low_value"],
                   high_value=options["high_value"],
                   max_problems=options["max_problems"],
                   timer=options["timer"],
                   timerval=options["timerval"],
                   stats=options["stats"]
                )
        assert game.gameover is False


class TestGameToDict:

    def test_to_dict_returns_dict(self):
        game = Game()
        assert isinstance(game.to_dict(), dict)

    def test_to_dict_default_values(self):
        game = Game()
        result = game.to_dict()
        assert result["name"] == "Flashcard Game"
        assert result["description"] == "A simple flashcard game."
        assert result["user"] == "Player"
        assert result["low_value"] == 0
        assert result["high_value"] == 20
        assert result["max_problems"] == 20
        assert result["timer"] is False
        assert result["timerval"] == 20
        assert result["stats"] is False
        assert result["correct_count"] == 0
        assert result["wrong_count"] == 0
        assert result["problem_count"] == 0
        assert result["current_problem_index"] == 0
        assert result["gameover"] is False
        assert result["problem"] == None

    def test_to_dict_operand_is_serialized_as_value(self):
        """Operand enum should be stored as its raw value, not the enum itself."""
        game = Game(operand=Operand.ADD)
        result = game.to_dict()
        assert result["operand"] == Operand.ADD.value
        assert not isinstance(result["operand"], Operand)

    def test_to_dict_contains_all_keys(self):
        expected_keys = {
            "running", "name", "description", "user", "low_value", "high_value",
            "operand", "max_problems", "timer", "timerval", "stats",
            "correct_count", "wrong_count", "problem_count",
            "current_problem_index","gameover", "problem",
        }
        result = Game().to_dict()
        assert set(result.keys()) == expected_keys

    def test_to_dict_custom_values(self):
        game = Game(user="Alan", low_value=1, high_value=12, operand=Operand.MULTIPLY, timer=True, timerval=30)
        result = game.to_dict()
        assert result["user"] == "Alan"
        assert result["low_value"] == 1
        assert result["high_value"] == 12
        assert result["operand"] == Operand.MULTIPLY.value
        assert result["timer"] is True
        assert result["timerval"] == 30

    def test_to_dict_with_problem(self):
        game = Game()
        gameproc = GameProcessor(game)
        problem = gameproc.get_problem_values(Operand.ADD)
        num1 = problem.number1
        num2 = problem.number2
        answer = problem.answer
        correct_answer = problem.correct_answer
        game.add_problem(problem)
        result = game.to_dict()
        assert result["problem_count"] == 1
        assert result["problem"]["operand"] == Operand.ADD.value
        assert result["problem"]["user_answer"] == 0
        assert result["problem"] == {"number1": num1, "number2": num2, "answer": answer, "correct_answer": correct_answer, "checked": False, "user_answer": 0, "operand": Operand.ADD.value}
       

    def test_to_dict_with_no_problems(self):
        game = Game()
        result = game.to_dict()
        assert result["problem"] == None
            
           

class TestGameFromDict:

    def _default_dict(self) -> dict:
        """Returns a valid dict matching Game defaults."""
        return Game().to_dict()

    def test_from_dict_returns_game_instance(self):
        result = Game.from_dict(self._default_dict())
        assert isinstance(result, Game)

    def test_from_dict_roundtrip(self):
        """to_dict → from_dict should produce an equal Game."""
        game = Game(user="Alan", low_value=1, high_value=12, operand=Operand.MULTIPLY)
        result = Game.from_dict(game.to_dict())
        assert result == game

    def test_from_dict_operand_is_deserialized_as_enum(self):
        data = self._default_dict()
        result = Game.from_dict(data)
        assert isinstance(result.operand, Operand)
        assert result.operand == Operand.ADD

    def test_from_dict_default_values(self):
        result = Game.from_dict(self._default_dict())
        assert result.name == "Flashcard Game"
        assert result.user == "Player"
        assert result.low_value == 0
        assert result.high_value == 20
        assert result.correct_count == 0
        assert result.problem is None

    def test_from_dict_custom_values(self):
        data = self._default_dict()
        data.update({"user": "Alan", "low_value": 1, "high_value": 12, "timer": True})
        result = Game.from_dict(data)
        assert result.user == "Alan"
        assert result.low_value == 1
        assert result.high_value == 12
        assert result.timer is True

    def test_from_dict_raises_on_missing_key(self):
        data = self._default_dict()
        del data["operand"]
        with pytest.raises(KeyError):
            Game.from_dict(data)

    def test_from_dict_raises_on_invalid_operand(self):
        data = self._default_dict()
        data["operand"] = "invalid"
        with pytest.raises(ValueError):
            Game.from_dict(data)

class TestProblems:
    
    def test_operand_addition(self): # NEED TO FIGURE OUT WHAT IS IN GAME AND WHAT IS IN PROBLEM
        gameproc = GameProcessor(Game(low_value=0, high_value=20))
        problem = gameproc.get_problem_values(operand=Operand.ADD)
        assert problem.number1 >= gameproc.game.low_value and problem.number1 <= gameproc.game.high_value
        assert problem.number2 >= gameproc.game.low_value and problem.number2 <= gameproc.game.high_value
        assert problem.answer == problem.number1 + problem.number2
        assert problem.operand == "+"
        
       
    def test_operand_subtraction(self):
        gameproc = GameProcessor(Game(low_value=0, high_value=20))
        problem = gameproc.get_problem_values(operand=Operand.SUBTRACT)
        assert problem.number1 >= gameproc.game.low_value and problem.number1 <= gameproc.game.high_value
        assert problem.number2 >= gameproc.game.low_value and problem.number2 <= gameproc.game.high_value
        assert problem.number1 >= problem.number2
        assert problem.answer == problem.number1 - problem.number2
        assert problem.operand == "-"

    def test_operand_multiplication(self):
        gameproc = GameProcessor(Game(low_value=0, high_value=20))
        problem = gameproc.get_problem_values(operand=Operand.MULTIPLY)
        assert problem.number1 >= gameproc.game.low_value and problem.number1 <= gameproc.game.high_value
        assert problem.number2 >= gameproc.game.low_value and problem.number2 <= gameproc.game.high_value
        assert problem.answer == problem.number1 * problem.number2
        assert problem.operand == "*"

    def test_operand_division(self):
        gameproc = GameProcessor(Game(low_value=1, high_value=20))
        problem = gameproc.get_problem_values(operand=Operand.DIVIDE)
        assert problem.number1 >= gameproc.game.low_value and problem.number1 <= gameproc.game.high_value
        assert problem.number2 >= gameproc.game.low_value and problem.number2 <= gameproc.game.high_value
        assert problem.number2 != 0
        assert problem.answer == problem.number1 // problem.number2
        assert problem.operand == "/"

    def test_operand_plusminus(self):
        gameproc = GameProcessor(Game(low_value=0, high_value=20))
        problem = gameproc.get_problem_values(operand=Operand.PLUSMINUS)
        assert problem.number1 >= gameproc.game.low_value and problem.number1 <= gameproc.game.high_value
        assert problem.number2 >= gameproc.game.low_value and problem.number2 <= gameproc.game.high_value
        assert problem.answer == problem.number1 + problem.number2 or problem.answer == problem.number1 - problem.number2
        assert problem.operand == "+" or problem.operand == "-"

    def test_operand_multdiv(self):
        gameproc = GameProcessor(Game(low_value=0, high_value=20))
        problem = gameproc.get_problem_values(operand=Operand.MULTDIV)
        assert problem.number1 >= gameproc.game.low_value and problem.number1 <= gameproc.game.high_value
        assert problem.number2 >= gameproc.game.low_value and problem.number2 <= gameproc.game.high_value
        assert problem.answer == problem.number1 * problem.number2 or problem.answer == problem.number1 // problem.number2
        assert problem.operand == "*" or problem.operand == "/"
    def test_operand_random(self):
        gameproc = GameProcessor(Game(low_value=0, high_value=20))
        problem = gameproc.get_problem_values(operand=Operand.RANDOM)
        assert problem.number1 >= gameproc.game.low_value and problem.number1 <= gameproc.game.high_value
        assert problem.number2 >= gameproc.game.low_value and problem.number2 <= gameproc.game.high_value
        assert problem.answer == problem.number1 +problem.number2 or problem.answer == problem.number1 -problem.number2 or problem.answer == problem.number1 * problem.number2 or problem.answer == problem.number1 //problem.number2
        assert problem.operand == "+" or problem.operand == "-" or problem.operand == "/" or problem.operand == "*"

    def test_add_problem_game(self):
        game = Game(low_value=0, high_value=20)
        gameproc = GameProcessor(game)
        problem = gameproc.get_problem_values(operand=Operand.ADD)
        game.add_problem(problem)
        assert game.problem is not None
        assert gameproc.game.problem == problem
        assert game.problem.number1 >= game.low_value
        assert game.problem.number2 >= game.low_value
        assert game.problem.number1 <= game.high_value
        assert game.problem.number2 <= game.high_value
        assert game.problem.answer == (game.problem.number1 +game.problem.number2)
        assert game.problem.operand.value == Operand.ADD.value

 
    def test_check_problem_correct(self):
        game = Game(low_value=0, high_value=20)
        gameproc = GameProcessor(game)
        problem = gameproc.get_problem_values(operand=Operand.ADD)
        game.add_problem(problem)
        correct = game.check_problem(answer=problem.answer, problem=problem)
        assert correct is True
        assert problem.checked is True
        assert problem.correct_answer is True
        assert game.correct_count == 1
        assert game.wrong_count == 0

    def test_check_problem_incorrect(self):
            game = Game(low_value=0, high_value=20)
            gameproc = GameProcessor(game)
            problem = gameproc.get_problem_values(operand=Operand.ADD)
            game.add_problem(problem)
            correct = game.check_problem(answer=problem.answer + 1, problem=problem)
            assert correct is False
            assert problem.checked is True
            assert problem.correct_answer is False
            assert game.correct_count == 0
            assert game.wrong_count == 1

class TestProblemToDict:

    def test_to_dict_returns_dict(self):
        assert isinstance(Problem().to_dict(), dict)

    def test_to_dict_contains_all_keys(self):
        expected_keys = {"number1", "number2", "answer", "correct_answer", "checked", "user_answer", "operand"}
        assert set(Problem().to_dict().keys()) == expected_keys

    def test_to_dict_operand_is_serialized_as_value(self):
        problem = Problem(operand=Operand.ADD)
        result = problem.to_dict()
        assert result["operand"] == Operand.ADD.value
        assert not isinstance(result["operand"], Operand)

    def test_to_dict_default_values(self):
        result = Problem().to_dict()
        assert result["number1"] == 0
        assert result["number2"] == 0
        assert result["answer"] == 0
        assert result["correct_answer"] == False
        assert result["checked"] == False
        assert result["user_answer"] == 0
        assert result["operand"] == Operand.ADD.value


class TestProblemFromDict:

    def test_from_dict_returns_problem_instance(self):
        result = Problem.from_dict(Problem().to_dict())
        assert isinstance(result, Problem)

    def test_from_dict_roundtrip(self):
        problem = Problem(number1=3, number2=4, answer=7, operand=Operand.ADD)
        assert Problem.from_dict(problem.to_dict()) == problem

    def test_from_dict_operand_is_deserialized_as_enum(self):
        result = Problem.from_dict(Problem().to_dict())
        assert isinstance(result.operand, Operand)

    def test_from_dict_raises_on_missing_key(self):
        data = Problem().to_dict()
        del data["answer"]
        with pytest.raises(KeyError):
            Problem.from_dict(data)

    def test_from_dict_raises_on_invalid_operand(self):
        data = Problem().to_dict()
        data["operand"] = "invalid"
        with pytest.raises(ValueError):
            Problem.from_dict(data)

class TestOptionsFromDict:

    def test_from_dict_returns_options_instance(self):
        result = Options.from_dict(Options().to_dict())
        assert isinstance(result, Options)

    def test_from_dict_roundtrip(self):
        options = Options(operand="+", low_value=0, high_value=20, max_problems=20, timer=False, timerval=20, stats=False)
        assert Options.from_dict(options.to_dict()) == options

    def test_from_dict_raises_on_missing_key(self):
        data = Options().to_dict()
        del data["operand"]
        with pytest.raises(KeyError):
            Options.from_dict(data)

class TestOptionsToDict:

    def test_to_dict_returns_dict(self):
        assert isinstance(Options().to_dict(), dict)

    def test_to_dict_contains_all_keys(self):
        expected_keys = {"operand", "low_value", "high_value", "max_problems", "timer", "timerval", "stats"}
        assert set(Options().to_dict().keys()) == expected_keys

    def test_to_dict_custom_values(self):
        options = Options(Operand.ADD, low_value=5, high_value=10, max_problems=10, timer=True, timerval=30, stats=True)
        result = options.to_dict()
        assert result["operand"] == Operand.ADD.value
        assert result["low_value"] == 5
        assert result["high_value"] == 10
        assert result["max_problems"] == 10
        assert result["timer"] == True
        assert result["timerval"] == 30
        assert result["stats"] == True