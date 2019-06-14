from view import (ViewServerMixin, ViewClientMixin,
         ViewGameState, ViewPlayer)

class ViewCLI(ViewServerMixin, ViewClientMixin):
    def __init__(self, owner):
        self.game_state = ViewGameState(owner=owner)

    def setup(self, players, current_player, hand, deck_size, offering, discard):
        gs = self.game_state
        gs.players = players
        gs.current_player = current_player
        gs.hand = hand
        gs.deck_size = deck_size
        gs.offering = offering
        gs.discard = discard

    def update(self, game_state):
        self.game_state.update(game_state)
        pass

    def render(self, game_state):
        pass

    def other_player_string(self, player):
        """
        Print a string representation of the player without any private info,
        such as cards in hand.
        """
        return """PLAYER:{:<20}     HAND:{:>2} CARDS\nFIELDS:{}""".format(
                player.name,
                player.hand_size,
                player.fields)

