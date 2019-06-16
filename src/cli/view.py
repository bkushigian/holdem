from view import (ViewServerMixin, ViewClientMixin,
         ViewGameState, ViewPlayer)

class ViewCLI(ViewServerMixin, ViewClientMixin):
    """
        A simple test view through a CLI. There is only a single CLI built for
        all players.
    """
    def __init__(self, formatter=None):
        self.game_state = ViewGameState()
        self.formatter = formatter
        if formatter is None:
            self.formatter = Formatter()

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
        print(str(self.formatter))

class Formatter:
    def __init__(self, view):
        self.view = view
        self.game_state = view.game_state

    def other_player_string(self, player):
        """
        Print a string representation of the player without any private info,
        such as cards in hand.
        """
        return """PLAYER:{:<20}     HAND:{:>2} CARDS\nFIELDS:{}""".format(
                player.name,
                player.hand_size,
                player.fields)

    def offering_string(self):
        """
        Print a string representation of the offering
        """
        return "OFFERING: {}".format(self.game_state.offering)

    def discard_string(self):
        d = self.game_state.discard
        return "DISCARD: {}, ...".format(d[0:min(len(d), 3)])

    def deck_string(self):
        return "DECK: {} CARDS".format(self.game_state.deck)

    def owner_string(self):
        return "YOUR HAND:{}\nYOUR FIELDS:{}".format(
                self.game_state.hand,
                self.game_state.players[self.game_state.owner()].fields)

    def __str__(self):
        gs = self.game_state
        data = []
        for i, p in gs:
            if i == gs.current_player: continue
            data.append(self.other_player_string(p))
        data.append(offering_string())
        data.append(discard_string())
        data.append(deck_string())
        data.append(owner_string())

        return '\n\n'.join(data)
