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
        self.assertEqual(game.error, None)
        d = {'action': 'harvest', 'args': (2, 0)}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)

    def test_harvest_2(self):
        game = self.new_game()
        game.players[0].fields[0] = (Card.cards[0], 3)
        d = {'action': 'harvest', 'args': (0, 0)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        self.assertEqual(game.players[0].coins, 0)
        self.assertEqual(game.error, None)

        game.players[0].fields[0] = (Card.cards[0], 4)
        d = {'action': 'harvest', 'args': (0, 0)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        self.assertEqual(game.players[0].coins, 1)
        self.assertEqual(game.error, None)

        game.players[0].fields[0] = (Card.cards[0], 5)
        d = {'action': 'harvest', 'args': (0, 0)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        self.assertEqual(game.players[0].coins, 2)
        self.assertEqual(game.error, None)

        game.players[0].fields[0] = (Card.cards[0], 13)
        d = {'action': 'harvest', 'args': (0, 0)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        self.assertEqual(game.players[0].coins, 6)
        self.assertEqual(game.error, None)

        game.players[1].fields[1] = (Card.cards[3], 2)
        d = {'action': 'harvest', 'args': (1, 1)}
        game.phase.update(**d)
        self.assertEqual(game.players[1].fields[1], None)
        self.assertEqual(game.players[1].coins, 0)
        self.assertEqual(game.error, None)

        game.players[1].fields[1] = (Card.cards[3], 3)
        d = {'action': 'harvest', 'args': (1, 1)}
        game.phase.update(**d)
        self.assertEqual(game.players[1].fields[1], None)
        self.assertEqual(game.players[1].coins, 1)
        self.assertEqual(game.error, None)

        game.players[1].fields[1] = (Card.cards[3], 5)
        d = {'action': 'harvest', 'args': (1, 1)}
        game.phase.update(**d)
        self.assertEqual(game.players[1].fields[1], None)
        self.assertEqual(game.players[1].coins, 2)
        self.assertEqual(game.error, None)

        game.players[0].fields[2] = (Card.cards[0], 7)
        d = {'action': 'harvest', 'args': (0, 2)}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields[0], None)
        self.assertEqual(game.players[0].coins, 8)
        self.assertEqual(game.error, None)

    def test_phase1_end_phase(self):
        game = self.new_game()
        game.phase = game.phase.next.next.next
        game.offering = [(Card.cards[0], 2), None, (Card.cards[1], 1)]

        d = {'action': 'next', 'args': None}
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

        self.assertEqual(game.error, None)

        game.offering = [(Card.cards[0], 2), None, (Card.cards[1], 1)]
        game.players[0].fields = [None, None, (Card.cards[1], 1)]
        d = {'action': 'plant', 'args': [0, 1, 2]}
        game.phase.update(**d)

        # Does nothing, raises error
        self.assertEqual(game.offering, [(Card.cards[0], 2), None, (Card.cards[1], 1)])
        self.assertEqual(game.players[0].fields, [None, None, (Card.cards[1], 1)])
        self.assertNotEqual(game.error, None)

        d = {'action': 'plant', 'args': [3]}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)

        game.offering = [(Card.cards[0], 2), None, (Card.cards[1], 1)]
        game.players[0].fields = [(Card.cards[0], 1), (Card.cards[2], 1), (Card.cards[3], 1)]
        d = {'action': 'plant', 'args': [0, 2]}
        game.phase.update(**d)

        # Does nothing, raises error
        self.assertEqual(game.offering, [(Card.cards[0], 2), None, (Card.cards[1], 1)])
        self.assertEqual(game.players[0].fields, [(Card.cards[0], 1), (Card.cards[2], 1), (Card.cards[3], 1)])
        self.assertNotEqual(game.error, None)

    def test_phase2_end_phase(self):
        game = self.new_game()

        # Try to end phase without planting
        d = {'action': 'next', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)

        # Plant, then try to end phase
        d = {'action': 'plant', 'args': None}
        game.phase.update(**d)
        d = {'action': 'next', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertIsInstance(game.phase, PhaseIII)

        phase2 = game.phase.next.next.next
        self.assertEqual(phase2.num_planted, 0)
        self.assertEqual(phase2.done_discarding, False) # this shouldn't have changed during the turn anyway b/c didn't discard

        # Plant, then discard, then try to end phase
        game = self.new_game()

        d = {'action': 'plant', 'args': None}
        game.phase.update(**d)
        d = {'action': 'discard', 'args': 0}
        game.phase.update(**d)
        self.assertEqual(game.phase.done_discarding, True)
        d = {'action': 'next', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertIsInstance(game.phase, PhaseIII)

        phase2 = game.phase.next.next.next
        self.assertEqual(phase2.num_planted, 0)
        self.assertEqual(phase2.done_discarding, False)

    def test_phase2_plant(self):
        game = self.new_game()
        game.players[0].hand = [Card.cards[0], Card.cards[1], Card.cards[2], Card.cards[3], Card.cards[4]]
        game.players[0].fields = [None, (Card.cards[4], 1), None]
        d = {'action': 'plant', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertEqual(game.players[0].fields, [None, (Card.cards[4], 2), None])
        self.assertEqual(game.players[0].hand, [Card.cards[0], Card.cards[1], Card.cards[2], Card.cards[3]])
        d = {'action': 'plant', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertEqual(game.players[0].fields, [(Card.cards[3], 1), (Card.cards[4], 2), None])
        self.assertEqual(game.players[0].hand, [Card.cards[0], Card.cards[1], Card.cards[2]])

        # Max already planted, shouldn't work
        d = {'action': 'plant', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)
        self.assertEqual(game.players[0].fields, [(Card.cards[3], 1), (Card.cards[4], 2), None])
        self.assertEqual(game.players[0].hand, [Card.cards[0], Card.cards[1], Card.cards[2]])

        # Test what happens if try to plant but no room
        game = self.new_game()
        game.players[0].hand = [Card.cards[0], Card.cards[1], Card.cards[2], Card.cards[3], Card.cards[4]]
        game.players[0].fields = [(Card.cards[0], 1), (Card.cards[1], 1), (Card.cards[2], 1)]
        d = {'action': 'plant', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)
        self.assertEqual(game.players[0].fields, [(Card.cards[0], 1), (Card.cards[1], 1), (Card.cards[2], 1)])
        self.assertEqual(game.players[0].hand,
                         [Card.cards[0], Card.cards[1], Card.cards[2], Card.cards[3], Card.cards[4]])

        # Try to discard before planting again
        d = {'action': 'harvest', 'args': (0, 0)}
        game.phase.update(**d)
        d = {'action': 'plant', 'args': None}
        game.phase.update(**d)
        d = {'action': 'discard', 'args': 0}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertEqual(game.phase.done_discarding, True)
        self.assertEqual(game.players[0].fields, [(Card.cards[4], 1), (Card.cards[1], 1), (Card.cards[2], 1)])
        self.assertEqual(game.players[0].hand, [Card.cards[1], Card.cards[2], Card.cards[3]])
        d = {'action': 'plant', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)
        self.assertEqual(game.players[0].fields, [(Card.cards[4], 1), (Card.cards[1], 1), (Card.cards[2], 1)])
        self.assertEqual(game.players[0].hand, [Card.cards[1], Card.cards[2], Card.cards[3]])
        self.assertEqual(game.phase.done_discarding, True)

        # Test if try to plant with no cards in hand
        game = self.new_game()
        game.players[0].hand = []
        game.players[0].fields = [None, None, None]
        d = {'action': 'plant', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)
        self.assertEqual(game.players[0].fields, [None, None, None])
        self.assertEqual(game.players[0].hand, [])

    def test_phase2_discard(self):

        # Shouldn't be able to discard if haven't planted yet
        game = self.new_game()
        game.players[0].hand = [Card.cards[0], Card.cards[1], Card.cards[2], Card.cards[3], Card.cards[4]]
        d = {'action': 'discard', 'args': 1}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)
        self.assertEqual(game.players[0].hand,
                         [Card.cards[0], Card.cards[1], Card.cards[2], Card.cards[3], Card.cards[4]])
        self.assertEqual(game.discard, [])

        # Should be able to discard after planting...
        d = {'action': 'plant', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.phase.done_discarding, False)

        # ... but not if index is invalid...
        d = {'action': 'discard', 'args': 4}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)
        self.assertEqual(game.players[0].hand, [Card.cards[0], Card.cards[1], Card.cards[2], Card.cards[3]])
        self.assertEqual(game.discard, [])
        self.assertEqual(game.phase.done_discarding, False)

        # ... or not an int
        d = {'action': 'discard', 'args': 'string'}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)
        self.assertEqual(game.players[0].hand, [Card.cards[0], Card.cards[1], Card.cards[2], Card.cards[3]])
        self.assertEqual(game.discard, [])
        self.assertEqual(game.phase.done_discarding, False)

        # Works if try again with valid index
        d = {'action': 'discard', 'args': 1}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertEqual(game.players[0].hand, [Card.cards[0], Card.cards[2], Card.cards[3]])
        self.assertEqual(game.discard, [Card.cards[1]])
        self.assertEqual(game.phase.done_discarding, True)

        # Can't discard twice
        d = {'action': 'discard', 'args': 1}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)
        self.assertEqual(game.players[0].hand, [Card.cards[0], Card.cards[2], Card.cards[3]])
        self.assertEqual(game.discard, [Card.cards[1]])
        self.assertEqual(game.phase.done_discarding, True)

    def test_phase3_draw_plant(self):
        game = self.new_game()
        game.phase = game.phase.next
        game.deck[-6:] = [Card.cards[3], Card.cards[4], Card.cards[5], Card.cards[0], Card.cards[1], Card.cards[2]]

        self.assertEqual(game.phase.done_drawing, False)
        self.assertEqual(game.phase.game_over, False)

        # Draw [3 cards] to offering once
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertEqual(game.offering, [(Card.cards[2], 1), (Card.cards[1], 1), (Card.cards[0], 1)])
        self.assertEqual(game.deck[-3:], [Card.cards[3], Card.cards[4], Card.cards[5]])
        self.assertEqual(len(game.deck), 131)
        self.assertEqual(game.phase.done_drawing, True)
        self.assertEqual(game.phase.game_over, False)

        # Shouldn't be able to draw twice
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)
        self.assertEqual(len(game.deck), 131)
        self.assertEqual(game.offering, [(Card.cards[2], 1), (Card.cards[1], 1), (Card.cards[0], 1)])
        self.assertEqual(game.phase.done_drawing, True)
        self.assertEqual(game.phase.game_over, False)

        # Should make a pile if two cards drawn are the same
        game = self.new_game()
        game.phase = game.phase.next
        game.deck[-6:] = [Card.cards[3], Card.cards[4], Card.cards[5], Card.cards[0], Card.cards[2], Card.cards[2]]

        self.assertEqual(game.phase.done_drawing, False)
        self.assertEqual(game.phase.game_over, False)
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertEqual(game.offering, [(Card.cards[2], 2), (Card.cards[0], 1), None])
        self.assertEqual(game.deck[-3:], [Card.cards[3], Card.cards[4], Card.cards[5]])
        self.assertEqual(len(game.deck), 131)
        self.assertEqual(game.phase.done_drawing, True)
        self.assertEqual(game.phase.game_over, False)

        # if top of discard matches cards in offering, should take those cards too
        game = self.new_game()
        game.phase = game.phase.next
        game.deck[-6:] = [Card.cards[3], Card.cards[4], Card.cards[5], Card.cards[0], Card.cards[2], Card.cards[2]]
        game.discard = [Card.cards[5], Card.cards[0], Card.cards[2]]

        self.assertEqual(game.phase.done_drawing, False)
        self.assertEqual(game.phase.game_over, False)
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertEqual(game.offering, [(Card.cards[2], 3), (Card.cards[0], 2), None])
        self.assertEqual(game.deck[-3:], [Card.cards[3], Card.cards[4], Card.cards[5]])
        self.assertEqual(game.discard, [Card.cards[5]])
        self.assertEqual(len(game.deck), 131)
        self.assertEqual(game.phase.done_drawing, True)
        self.assertEqual(game.phase.game_over, False)

        # if run out of cards in deck, game_over flag should be set
        game = self.new_game()
        game.phase = game.phase.next
        game.deck = [Card.cards[0], Card.cards[2]]
        game.discard = [Card.cards[5], Card.cards[0], Card.cards[2]]

        self.assertEqual(game.phase.done_drawing, False)
        self.assertEqual(game.phase.game_over, False)
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertEqual(game.offering, [(Card.cards[2], 2), (Card.cards[0], 2), None])
        self.assertEqual(game.deck, [])
        self.assertEqual(game.discard, [Card.cards[5]])
        self.assertEqual(game.phase.done_drawing, True)
        self.assertEqual(game.phase.game_over, True)

        # planting should work even though game over
        d = {'action': 'plant', 'args': [0]}
        game.phase.update(**d)
        self.assertEqual(game.players[0].fields, [(Card.cards[2], 2), None, None])
        self.assertEqual(game.offering, [None, (Card.cards[0], 2), None])
        self.assertEqual(game.phase.done_drawing, True)
        self.assertEqual(game.phase.game_over, True)

        # Not including thorough testing of planting because did so for phase1


    def test_phase3_end_phase(self):
        game = self.new_game()
        game.phase = game.phase.next
        game.deck[-6:] = [Card.cards[3], Card.cards[4], Card.cards[5], Card.cards[0], Card.cards[1], Card.cards[2]]

        self.assertEqual(game.phase.done_drawing, False)
        self.assertEqual(game.phase.game_over, False)

        # Shouldn't be able to end phase without drawing
        d = {'action': 'next', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)
        self.assertIsInstance(game.phase, PhaseIII)
        self.assertEqual(game.offering, [None, None, None])
        self.assertEqual(game.deck[-6:],
                         [Card.cards[3], Card.cards[4], Card.cards[5], Card.cards[0], Card.cards[1], Card.cards[2]])
        self.assertEqual(len(game.deck), 134)
        self.assertEqual(game.phase.done_drawing, False)
        self.assertEqual(game.phase.game_over, False)

        # Ending phase after drawing should work
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        d = {'action': 'next', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertIsInstance(game.phase, PhaseIV)
        self.assertEqual(len(game.deck), 131)
        self.assertEqual(game.offering, [(Card.cards[2], 1), (Card.cards[1], 1), (Card.cards[0], 1)])
        self.assertEqual(game.phase.next.next.next.done_drawing, False)
        self.assertEqual(game.phase.next.next.next.game_over, False)

        # ending phase with game over should result in phase_game_over
        game = self.new_game()
        game.phase = game.phase.next
        game.deck = [Card.cards[0], Card.cards[2]]
        game.players[0].fields = [(Card.cards[0], 6), None, (Card.cards[1], 3)]
        game.players[1].fields = [None, (Card.cards[2], 7), None]
        # results in game over because deck is empty
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        d = {'action': 'next', 'args': None}
        game.phase.update(**d)
        self.assertIsInstance(game.phase, PhaseGameOver)
        self.assertEqual(game.players[0].coins, 1)
        self.assertEqual(game.players[1].coins, 2)
        self.assertEqual(game.discard, [Card.cards[0], Card.cards[0], Card.cards[0], Card.cards[0], Card.cards[0],
                                        Card.cards[1], Card.cards[1], Card.cards[1],
                                        Card.cards[2], Card.cards[2], Card.cards[2], Card.cards[2], Card.cards[2]])
        self.assertEqual(game.players[0].fields, [None, None, None])
        self.assertEqual(game.players[1].fields, [None, None, None])

    def test_phase4_draw(self):

        # Draw should work under normal circumstances
        game = self.new_game()
        game.phase = game.phase.next.next
        game.deck[-6:] = [Card.cards[3], Card.cards[4], Card.cards[5], Card.cards[0], Card.cards[1], Card.cards[2]]
        game.players[0].hand = [Card.cards[0], Card.cards[1], Card.cards[2]]
        self.assertEqual(game.phase.done_drawing, False)
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.players[0].hand,
                         [Card.cards[1], Card.cards[2], Card.cards[0], Card.cards[1], Card.cards[2]])
        self.assertEqual(game.deck[-4:], [Card.cards[3], Card.cards[4], Card.cards[5], Card.cards[0]])
        self.assertEqual(len(game.deck), 132)
        self.assertEqual(game.error, None)
        self.assertEqual(game.phase.done_drawing, True)

        # Shouldn't be able to draw twice
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.players[0].hand,
                         [Card.cards[1], Card.cards[2], Card.cards[0], Card.cards[1], Card.cards[2]])
        self.assertEqual(game.deck[-4:], [Card.cards[3], Card.cards[4], Card.cards[5], Card.cards[0]])
        self.assertEqual(len(game.deck), 132)
        self.assertNotEqual(game.error, None)
        self.assertEqual(game.phase.done_drawing, True)

        # If only one card left in deck
        game = self.new_game()
        game.phase = game.phase.next.next
        game.deck = [Card.cards[2]]
        game.players[0].hand = [Card.cards[0], Card.cards[1], Card.cards[2]]
        self.assertEqual(game.phase.done_drawing, False)
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.players[0].hand,
                         [Card.cards[2], Card.cards[0], Card.cards[1], Card.cards[2]])
        self.assertEqual(game.deck, [])
        self.assertEqual(game.error, None)
        self.assertIsInstance(game.phase, PhaseGameOver)

        # If no cards left in deck
        game = self.new_game()
        game.phase = game.phase.next.next
        game.deck = []
        game.players[0].hand = [Card.cards[0], Card.cards[1], Card.cards[2]]
        self.assertEqual(game.phase.done_drawing, False)
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.players[0].hand,
                         [Card.cards[0], Card.cards[1], Card.cards[2]])
        self.assertEqual(game.deck, [])
        self.assertEqual(game.error, None)
        self.assertIsInstance(game.phase, PhaseGameOver)

        # already tested game_over() for phase3

    def test_phase4_end_phase(self):

        game = self.new_game()
        game.phase = game.phase.next.next

        # Shouldn't be able to end phase if haven't drawn
        d = {'action': 'next', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)

        # End phase should work if have already drawn
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        d = {'action': 'next', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.error, None)
        self.assertIsInstance(game.phase, PhaseI)
        self.assertEqual(game.phase.next.next.next.done_drawing, False)
        self.assertEqual(game.curr_player, 1)

        # Changing curr_player should work if curr_player = 1
        game = self.new_game()
        game.phase = game.phase.next.next
        game.curr_player = 1
        d = {'action': 'draw', 'args': None}
        game.phase.update(**d)
        d = {'action': 'next', 'args': None}
        game.phase.update(**d)
        self.assertEqual(game.curr_player, 0)

    def test_invalid_action(self):

        game = self.new_game()
        d = {'action': 'wrong', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)

        game.phase = game.phase.next
        d = {'action': 'wrong', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)

        game.phase = game.phase.next
        d = {'action': 'wrong', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)

        game.phase = game.phase.next
        d = {'action': 'wrong', 'args': None}
        game.phase.update(**d)
        self.assertNotEqual(game.error, None)
