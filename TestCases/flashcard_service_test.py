import pytest 
import logging
from services.flashcard_service import Game, GameProcessor, Operand, Problem


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


class TestProblems:
    
    def test_operand_addition(self): # NEED TO FIGURE OUT WHAT IS IN GAME AND WHAT IS IN PROBLEM
        gameproc = GameProcessor(Game(low_value=0, high_value=20))
        problem = GameProcessor.get_problem_values(self=None, gameproc=gameproc, Operand=Operand.ADD)
        assert problem.number1 >= gameproc.game.low_value and problem.number1 <= gameproc.game.high_value
        assert problem.number2 >= gameproc.game.low_value and problem.number2 <= gameproc.game.high_value
        assert problem.answer == problem.number1 + problem.number2
        assert problem.operand == Operand.ADD
        
       
    def test_operand_subtraction(self):
        gameproc = GameProcessor(Game(low_value=0, high_value=20))
        problem = GameProcessor.get_problem_values(self=None, gameproc=gameproc, Operand=Operand.SUBTRACT)
        assert problem.number1 >= gameproc.game.low_value and problem.number1 <= gameproc.game.high_value
        assert problem.number2 >= gameproc.game.low_value and problem.number2 <= gameproc.game.high_value
        assert problem.number1 >= problem.number2
        assert problem.answer == problem.number1 - problem.number2
        assert problem.operand == Operand.SUBTRACT

    def test_operand_multiplication(self):
        gameproc = GameProcessor(Game(low_value=0, high_value=20))
        problem = GameProcessor.get_problem_values(self=None, gameproc=gameproc, Operand=Operand.MULTIPLY)
        assert problem.number1 >= gameproc.game.low_value and problem.number1 <= gameproc.game.high_value
        assert problem.number2 >= gameproc.game.low_value and problem.number2 <= gameproc.game.high_value
        assert problem.answer == problem.number1 * problem.number2
        assert problem.operand == Operand.MULTIPLY

    def test_operand_division(self):
        gameproc = GameProcessor(Game(low_value=1, high_value=20))
        problem = GameProcessor.get_problem_values(self=None, gameproc=gameproc, Operand=Operand.DIVIDE)
        assert problem.number1 >= gameproc.game.low_value and problem.number1 <= gameproc.game.high_value
        assert problem.number2 >= gameproc.game.low_value and problem.number2 <= gameproc.game.high_value
        assert problem.number2 != 0
        assert problem.answer == problem.number1 // problem.number2
        assert problem.operand == Operand.DIVIDE

    def test_add_problem_game(self):
        game = Game(low_value=0, high_value=20)
        gameproc = GameProcessor(game)
        problem = GameProcessor.get_problem_values(self=None, gameproc=gameproc, Operand=Operand.ADD)
        game.problems.append(problem)
        assert len(game.problems) == 1
        assert gameproc.game.problems[0] == problem
        assert game.problems[0].number1 >= game.low_value
        assert game.problems[0].number2 >= game.low_value
        assert game.problems[0].number1 <= game.high_value
        assert game.problems[0].number2 <= game.high_value
        assert game.problems[0].answer == game.problems[0].number1 + game.problems[0].number2
        assert game.problems[0].operand == Operand.ADD  
    