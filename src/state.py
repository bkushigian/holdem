"""
All things statey
"""


class Player:
    def __init__(self):
        self.fields = [[], [], []]


class Card:
    cards = []

    def __init__(self, name, exchange, count):
        """
        Create a new singleton card
        :param name: name of the card
        :param exchange: length 4 list representing the number of harvested
            beans needed to get  1, 2, 3, or 4 coins respectively
        :param count: number of cards in the deck
        """
        self.name = name
        self.count = count
        self.exchange = {}
        # TODO: Turn exchange into map self.exchange
        Card.cards.append(self)


class Game:
    def __init__(self):
        self.num_players = 2
        self.players = [Player(), Player()]
        self.deck = []     # TODO
        self.discard = []


Card(name="Coffee Bean", exchange=(4, 7, 10, 12), count=24)

