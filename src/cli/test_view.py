from unittest import TestCase
from cli.view import ViewCLI
from state import Player, Card, Game, Phase

owner = "Boaty McBoatface"

class TestCLIView(TestCase):
    def setUp(self):
        self.bview = ViewCLI("Ben")
        self.kview = ViewCLI("Kathryn")
        players = [Player("Ben"), Player("Kathryn")]
        # self.game =

    def test_constructor(self):
        pass

    def test_setup(self):
        pass
