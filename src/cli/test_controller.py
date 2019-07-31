from unittest import TestCase
from state import *
from model import Model
from cli.controller import ControllerCLI
from cli.view import ViewCLI
from view import ViewGameState


class TestModel(TestCase):

    def setup(self):
        player1 = Player('Ben')
        player2 = Player('Kate')
        game = Game([player1, player2])
        model = Model(game)


        for i in range(len(game.players)):
            model.register_view(ViewCLI(ViewGameState.from_game(game, i)))

        controller = ControllerCLI(model, model.views[0])  # ??? Don't know what else to do