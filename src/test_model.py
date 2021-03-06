from unittest import TestCase
from game import *
from model import Model


class TestModel(TestCase):
    def new_game(self):
        player1 = Player('Ben')
        player2 = Player('Kate')
        g = Game([player1, player2])
        m = Model(g)
        return m

    def test_model_init(self):
        m = self.new_game()
        p1_hand = m.views[0].game_state.hand
        p2_hand = m.views[1].game_state.hand

        print(p1_hand)
        print(p2_hand)
        self.assertEqual(len(p1_hand), 5)
        self.assertEqual(len(p2_hand), 5)

        p2_other_hand = m.views[1].game_state.players[0].hand_size

        self.assertEqual(p2_other_hand, 5)

        m.game.players[0].hand = [Card.cards[0], Card.cards[1], Card.cards[2]]
        self.assertEqual(m.game.players[0].hand, [Card.cards[0], Card.cards[1], Card.cards[2]])
        m.update_views()

        p1_hand = m.views[0].game_state.hand
        p2_hand = m.views[1].game_state.hand

        print(p1_hand)
        print(p2_hand)
        self.assertEqual(len(p1_hand), 3)
        self.assertEqual(len(p2_hand), 5)

        p2_other_hand = m.views[1].game_state.players[0].hand_size

        self.assertEqual(p2_other_hand, 3)

    def test_model_draw_to_offering(self):
        # specifically, tests the CLI view
        m = self.new_game()
        m.game.phase = m.game.phase.next
        m.game.deck[-3:] = [Card.cards[6], Card.cards[6], Card.cards[6]]
        d = {'action': 'draw', 'args': None}
        m.game.phase.update(**d)
        for view in m.views:
            print(view.game_state.owner)
            view.render()    # change to offering is visible (because the game_state has a reference to the offering) but not change to deck size.
        m.update_views()
        for view in m.views:
            print(view.game_state.owner)
            view.render()
        d = {'action': 'plant', 'args': [0]}
        m.game.phase.update(**d)
        m.update_views()
        for view in m.views:
            print(view.game_state.owner)
            view.render()
        d = {'action': 'harvest', 'args': (0, 0)}
        m.game.phase.update(**d)
        m.update_views()
        for view in m.views:
            print(view.game_state.owner)
            view.render()
        m.game.phase = m.game.phase.next
        d = {'action': 'draw', 'args': None}
        m.game.phase.update(**d)
        m.update_views()
        for view in m.views:
            print(view.game_state.owner)
            view.render()
