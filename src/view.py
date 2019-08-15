class ViewServerMixin:
    """ Mixin for the server side of the View. """

    def __init__(self, game_state):
        """
        :param game_state: ViewGameState
        """

        pass

    def update(self, game_state):  # should this be filled out? 'if client is not this object'?
        """Update the game state and send to the client if the client is not
        this object."""
        raise NotImplementedError()


class ViewClientMixin:
    """ Mixin for the client side of the View.  """

    def render(self):
        """Render the newest version of the view"""
        raise NotImplementedError()


class ViewGameState:
    def __init__(self, owner, phase=None, players=None, current_player=None, hand=None,
                 deck_size=None, offering=None, discard=None, error=None, available_actions=None):
        """ Create a new game state to pass to the View. A default value of
        `None` is provided for each argument aside from `owner`, which must be
        specified by the caller. A value of `None` means that no update was made
        to that piece of game state and it needn't be sent to the `View`.

        :param owner: the index into `players` of the player who is being
            updated. This is to prevent sharing data, such as the player's hand,
            to other players
        :param phase: phase in the game
        :param players: a list of `ViewPlayer`s, which represents bean fields
            and hand sizes, as well as player names, etc.
        :param current_player: an index into `players` indicating whose turn it
            is.
        :param hand: the cards in `owner`'s hand
        :param deck_size: the number of cards remaining in the deck
        :param offering: the offering
        :param discard: the discard pile
        :param available_actions: the actions available to the active player
        """
        self.owner = owner
        self.phase = phase
        self.players = players
        self.current_player = current_player
        self.hand = hand
        self.deck_size = deck_size
        self.offering = offering
        self.discard = discard
        self.error = error
        self.available_actions = available_actions

    def update(self, other):
        """
        Update this `ViewGameState` with another. Take all non-`None` values as
        the new values, and retain all old values where `other` has `None`.

        Thus, if the only thing that happened since the last time game state was
        updated was that a player drew a card, that player's new hand size and
        the new deck size should be reported, but nothing else.
        """
        if other.phase is not None:
            self.phase = other.phase
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

        if other.players is not None:  # Added this
            self.players = other.players
        if other.available_actions is not None:
            self.available_actions = other.available_actions
        self.error = other.error  # ??? because shouldn't carry over between updates, and needs to actually be None most of the time???

    @staticmethod
    def from_game(game, owner):
        hand = game.players[owner].hand
        phase = game.phase
        players = [ViewPlayer.from_player(player) for player in game.players]
        error = None  # ???
        if game.error is not None and (game.error.player == -1 or game.error.player == owner):
            error = game.error
        return ViewGameState(owner=owner,
                             phase=phase,
                             players=players,
                             current_player=game.curr_player,
                             hand=hand,
                             deck_size=len(game.deck),
                             offering=game.offering,
                             discard=game.discard,
                             error=error,
                             available_actions=phase.get_valid_actions())

    def __str__(self):
        return """ViewGameState(phase:{},owner:{},current_player:{},hand:{},deck_size:{},offering:{})""".format(
            self.phase, self.owner, self.current_player, self.hand, self.deck_size, self.offering
        )


class ViewPlayer:
    def __init__(self, name, hand_size, fields, coins):
        """
        Create a new player for sending to a `View`. This contains the player's
        name, their hand size, and their bean fields.
        :param name: the player's name
        :param hand_size: the player's hand size
        :param fields: a list of the player's bean fields
        :param coins: the number of coins the player has
        """
        self.name = name
        self.hand_size = hand_size
        self.fields = fields
        self.coins = coins

    @staticmethod
    def from_player(player):
        """using Game Player"""
        return ViewPlayer(player.name, len(player.hand), player.fields, player.coins)
