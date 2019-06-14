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

    def new_game(self):
        player1 = Player('Ben')
        player2 = Player('Kate')
        return Game([player1, player2])

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

    def test_harvest_1(self):
        game = self.new_game()
        d = {'action':'harvest', 'args':(0,0)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        self.assertEqual(game.status, 0)
        d = {'action': 'harvest', 'args': (2, 0)}
        game.phase.update(**d)
        self.assertEqual(game.status, 1)

    def test_harvest_2(self):
        game = self.new_game()
        game.players[0].fields[0] = (Card.cards[0], 3)
        d = {'action': 'harvest', 'args': (0, 0)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        self.assertEqual(game.players[0].coins, 0)
        self.assertEqual(game.status, 0)

        game.players[0].fields[0] = (Card.cards[0], 4)
        d = {'action': 'harvest', 'args': (0, 0)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        self.assertEqual(game.players[0].coins, 1)
        self.assertEqual(game.status, 0)

        game.players[0].fields[0] = (Card.cards[0], 5)
        d = {'action': 'harvest', 'args': (0, 0)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        self.assertEqual(game.players[0].coins, 2)
        self.assertEqual(game.status, 0)

        game.players[0].fields[0] = (Card.cards[0], 13)
        d = {'action': 'harvest', 'args': (0, 0)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        self.assertEqual(game.players[0].coins, 6)
        self.assertEqual(game.status, 0)

        game.players[1].fields[1] = (Card.cards[3], 2)
        d = {'action': 'harvest', 'args': (1, 1)}
        game.phase.update(**d)
        self.assertEqual(game.players[1].fields[1], None)
        self.assertEqual(game.players[1].coins, 0)
        self.assertEqual(game.status, 0)

        game.players[1].fields[1] = (Card.cards[3], 3)
        d = {'action': 'harvest', 'args': (1, 1)}
        game.phase.update(**d)
        self.assertEqual(game.players[1].fields[1], None)
        self.assertEqual(game.players[1].coins, 1)
        self.assertEqual(game.status, 0)

        game.players[1].fields[1] = (Card.cards[3], 5)
        d = {'action': 'harvest', 'args': (1, 1)}
        game.phase.update(**d)
        self.assertEqual(game.players[1].fields[1], None)
        self.assertEqual(game.players[1].coins, 2)
        self.assertEqual(game.status, 0)

        game.players[0].fields[2] = (Card.cards[0], 7)
        d = {'action': 'harvest', 'args': (0, 2)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        self.assertEqual(game.players[0].coins, 8)
        self.assertEqual(game.status, 0)

    def test_phase1_end_phase(self):
        game = self.new_game()
        game.phase = game.phase.next.next.next
        game.offering = [(Card.cards[0], 2), None, (Card.cards[1], 1)]

        d = {'action': 'end_phase', 'args': None}
        game.phase.update(**d)

        self.assertEqual(game.offering, [None, None, None])

        self.assertEqual(len(game.discard), 3)
        self.assertEqual(game.discard[0], Card.cards[0])
        self.assertEqual(game.discard[1], Card.cards[0])
        self.assertEqual(game.discard[2], Card.cards[1])

        self.assertIsInstance(game.phase, PhaseII)

    def test_phase1_plant(self):
        game = self.new_game()
        game.phase = game.phase.next.next.next
        game.offering = [(Card.cards[0], 2), None, (Card.cards[1], 1)]
        game.players[0].fields = [None, None, (Card.cards[1], 1)]
        d = {'action': 'plant', 'args': [0, 2]}
        game.phase.update(**d)

        self.assertEqual(game.offering, [None, None, None])
        self.assertEqual(game.players[0].fields, [(Card.cards[0], 2), None, (Card.cards[1], 2)])
        self.assertEqual(game.status, 0)

        game.offering = [(Card.cards[0], 2), None, (Card.cards[1], 1)]
        game.players[0].fields = [None, None, (Card.cards[1], 1)]
        d = {'action': 'plant', 'args': [0, 1, 2]}
        game.phase.update(**d)

        # Partly does what was asked, but doesn't finish due to error
        # Don't know if I like this behavior--maybe ignore if give index of empty offering?
        self.assertEqual(game.offering, [None, None, (Card.cards[1], 1)])
        self.assertEqual(game.players[0].fields, [(Card.cards[0], 2), None, (Card.cards[1], 1)])
        self.assertEqual(game.status, 1)

        d = {'action': 'plant', 'args': [3]}
        game.phase.update(**d)
        self.assertEqual(game.status, 1)

        game.offering = [(Card.cards[0], 2), None, (Card.cards[1], 1)]
        game.players[0].fields = [(Card.cards[0], 1), (Card.cards[2], 1), (Card.cards[3], 1)]
        d = {'action': 'plant', 'args': [0, 2]}
        game.phase.update(**d)

        # Partly does what was asked, but doesn't finish due to error
        self.assertEqual(game.offering, [None, None, (Card.cards[1], 1)])
        self.assertEqual(game.players[0].fields, [(Card.cards[0], 3), (Card.cards[2], 1), (Card.cards[3], 1)])
        self.assertEqual(game.status, 1)

    def test_phase2_end_phase(self):
        game = self.new_game()

        d = {'action': 'end_phase', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.status, 1)

        d = {'action': 'plant', 'args': None}
        game.phase.update(**d)
        d = {'action': 'end_phase', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.status, 0)
        self.assertIsInstance(game.phase, PhaseIII)

