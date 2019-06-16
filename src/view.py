class ViewServerMixin:
    """ Mixin for the server side of the View. """

    def update(self, game_state):
        """Update the game state and send to the client if the client is not
        this object."""
        pass

class ViewClientMixin:
    """ Mixin for the client side of the View.  """

    def render(self):
        """Render the newest version of the view"""
        pass

class ViewGameState:
    def __init__(self, owner, players=None, current_player=None, hand=None,
            deck_size=None, offering=None, discard=None):
        """ Create a new game state to pass to the View. A default value of
        `None` is provided for each argument aside from `owner`, which must be
        specified by the caller. A value of `None` means that no update was made
        to that piece of game state and it needn't be sent to the `View`.

        :param owner: the index into `players` of the player who is being
            updated. This is to prevent sharing data, such as the player's hand,
            to other players
        :param players: a list of `ViewPlayer`s, which represents bean fields
            and hand sizes, as well as player names, etc.
        :param current_player: an index into `players` indicating whose turn it
            is.
        :param hand: the cards in `owner`'s hand
        :param deck_size: the number of cards remaining in the deck
        :param offering: the offering
        :param discard: the discard pile
        """
        self.owner = owner
        self.players = players
        self.current_player = current_player
        self.hand = hand
        self.deck_size = deck_size
        self.offering = offering
        self.discard = discard

    def update(self, other):
        """
        Update this `ViewGameState` with another. Take all non-`None` values as
        the new values, and retain all old values where `other` has `None`.

        Thus, if the only thing that happened since the last time game state was
        updated was that a player drew a card, that player's new hand size and
        the new deck size should be reported, but nothing else.
        """
        if other.current_player is not None:
            self.current_player = other.current_player
        if other.hand is not None:
            self.hand = other.hand
        if other.deck_size is not None:
            self.deck_size = other.deck_size
        if other.offering is not None:
            self.offering = other.offering
        if other.discard is not None:
            self.discard = other.discard

    @staticmethod
    def from_game_state(self, game_state, owner):
        hand = game_state.players[owner].hand
        return ViewGameState(owner=owner,
                    players=game_state.players,
                    current_player=game_state.current_player,
                    hand=hand,
                    deck_size=len(game_state.deck),
                    offering=game_state.offering,
                    discard=game_state.discard)

class ViewPlayer:
    def __init__(self, name, hand_size, fields):
        """
        Create a new player for sending to a `View`. This contains the player's
        name, their hand size, and their bean fields.
        :param name: the player's name
        :param hand_size: the player's hand size
        :param fields: a list of the player's bean fields
        """
        self.name = name
        self.hand_size = hand_size
        self.fields = fields

