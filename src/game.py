"""
All things statey
"""
from cards import Card
from phases.pl2 import TwoPlayerPhases


class Player:
    def __init__(self, name):
        self.fields = [None, None, None]
        self.name = name
        self.coins = 0
        self.hand = []


class ErrorMessage:
    def __init__(self, player, msg):
        self.player = player    # -1 for all players?
        self.msg = msg

    def __str__(self):
        return self.msg


class Game:
    def __init__(self, players):

        self.num_players = len(players)
        self.players = players  # List of players in order of turns
        self.deck = self.new_deck()
        self.discard = []
        self.offering = [None, None, None]
        self.curr_player = 0

        self.error = None
        self.actions = []

        if len(players) == 2:
            self.phase = TwoPlayerPhases.PhaseI(self)
            self.phase_game_over = TwoPlayerPhases.PhaseGameOver(self)
            self.phase.create_phases()
            self.phase = self.phase.next

        else:
            raise RuntimeError("Only 2 player games supported ATM")

        for _ in range(5):
            for i in range(len(players)):
                self.deal_to_player(i)

    def new_deck(self):
        """
        Creates a new shuffled deck with the appropriate cards and returns it.
        A deck is represented as a list of `Card`s which are accessible from the
        `Card` class via `Card.cards`.

        For two player (the only version we are implementing currently) the
        Garden and Cocoa beans are removed.

        :return:
        """
        import random as r

        if len(self.players) != 2:
            raise RuntimeError("Only 2 player games supported ATM")

        deck = [card for card in Card.cards for _ in range(card.count)
                if card.name != 'Garden Bean' and card.name != 'Cocoa Bean']

        r.shuffle(deck)
        return deck

    def game_over(self):
        self.phase = self.phase_game_over
        for player in self.players:
            for field in player.fields:
                if field is None:
                    continue
                card, number = field
                coins = card[number]
                player.coins += coins
                self.discard.extend([card] * (number - coins))
            player.fields = [None] * len(player.fields)

    def deal_to_player(self, player):   # this is only used at start of game. can I change this/phase4 so it can be reused? complicated by gave_over
        if not self.deck:
            self.report_error(self.curr_player, "Deal from empty deck")
            return False
        self.players[player].hand.insert(0, self.deck.pop())

    def report_error(self, player, msg):   # now have field called error, too...
        self.error = ErrorMessage(player, msg)


