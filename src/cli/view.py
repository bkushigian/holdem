from view import (ViewServerMixin, ViewClientMixin,
         ViewGameState, ViewPlayer)


class ViewCLI(ViewServerMixin, ViewClientMixin):    # ViewServerMixin takes a game_state, not owner
    """
        A simple test view through a CLI. There is only a single CLI built for
        all players.
    """
    """
    def __init__(self, owner, formatter=None):  # added owner (not sure)
        self.game_state = ViewGameState(owner)   # why no owner arg?
        self.formatter = formatter
        if formatter is None:
            self.formatter = Formatter(self)
    """

    def __init__(self, game_state, formatter=None):  # added owner (not sure). need owner?
        self.game_state = game_state  # why no owner arg?
        self.formatter = formatter
        if formatter is None:
            self.formatter = Formatter(self)

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

    def render(self):
        print(str(self.formatter))

class Formatter:
    def __init__(self, view):                   # view is a ViewCLI?
        self.view = view
        self.game_state = view.game_state

    def other_player_string(self, player):
        """
        Print a string representation of the player without any private info,
        such as cards in hand.
        """
        return """PLAYER:{:<20}     HAND:{:>2} CARDS    COINS:{:>2}\nFIELDS:{}""".format(
                player.name,
                player.hand_size,
                player.coins,
                player.fields)

    def offering_string(self):
        """
        Print a string representation of the offering
        """
        return "OFFERING: {}".format(self.game_state.offering)

    def discard_string(self):
        d = self.game_state.discard
        return "DISCARD: ..., {}".format(d[-min(len(d), 3):])       # discard top is on right end?

    def deck_string(self):
        return "DECK: {} CARDS".format(self.game_state.deck_size)

    def owner_string(self):
        return "YOUR HAND:{}\nYOUR FIELDS:{}\nYOUR COINS:{}".format(
                self.game_state.hand,
                self.game_state.players[self.game_state.owner].fields,
                self.game_state.players[self.game_state.owner].coins)

    def __str__(self):
        gs = self.game_state
        data = []
        for i, p in enumerate(gs.players):  # changed. not sure
            if i == gs.owner: continue
            data.append(self.other_player_string(p))
        data.append(self.offering_string())
        data.append(self.discard_string())
        data.append(self.deck_string())
        data.append(self.owner_string())

        return '\n\n'.join(data)
