from unittest import TestCase
from state import *


class MockGame:
    def __init__(self):
        self.phase = PhaseI(self)
        self.phase.create_phases()

class TestGame(TestCase):
    def test_constructor(self):
        player1 = Player('Ben')
        player2 = Player('Kate')
        game = Game([player1, player2])
        self.assertEqual(len(game.players[0].hand), 5)
        self.assertEqual(len(game.players[0].hand), 5)
        self.assertIsInstance(game.players[0].hand[0], Card)
        self.assertEqual(len(game.deck), 134)

class TestPhase(TestCase):

    def test_blah(self):
        self.assertEqual(1, 1)

    def test_constructors(self):
        game = MockGame()
        phase = game.phase
        self.assertIsInstance(phase, PhaseI)
        phase = phase.next
        self.assertIsInstance(phase, PhaseII)
        phase = phase.next
        self.assertIsInstance(phase, PhaseIII)
        phase = phase.next
        self.assertIsInstance(phase, PhaseIV)
        phase = phase.next
        self.assertIsInstance(phase, PhaseI)

    def test_harvest(self):
        player1 = Player('Ben')
        player2 = Player('Kate')
        game = Game([player1, player2])
        d = {'action':'harvest', 'args':(0,0)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        d = {'action': 'harvest', 'args': (2, 0)}
        game.phase.update(**d)
        self.assertRaises(Exception)

