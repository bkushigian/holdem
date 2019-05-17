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


Card(name="Coffee Bean",        exchange=(4,    7, 10, 12),    count=24)
Card(name="Wax Bean",           exchange=(4,    7,  9, 11),    count=22)
Card(name="Blue Bean",          exchange=(4,    6,  8, 10),    count=20)
Card(name="Chili Bean",         exchange=(3,    6,  8,  9),    count=18)
Card(name="Stink Bean",         exchange=(3,    5,  7,  8),    count=16)
Card(name="Green Bean",         exchange=(3,    5,  6,  7),    count=14)
Card(name="Soy Bean",           exchange=(2,    4,  6,  7),    count=12)
Card(name="Black-eyed Bean",    exchange=(2,    4,  5,  6),    count=10)
Card(name="Red Bean",           exchange=(2,    3,  4,  5),    count=8)
Card(name="Garden Bean",        exchange=(None, 2,  3,  None), count=6)
Card(name="Cocoa Bean",         exchange=(None, 2,  3,  4),    count=4)
