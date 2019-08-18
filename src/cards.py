class Card:
    cards = []
    name_to_card = {}

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
        self._exchange = exchange
        self.exchange = {}
        self.max = 0

        # Turn exchange into map self.exchange
        curr_num_coins = 0
        curr_num_cards = 0
        for i in range(4):
            if exchange[i] is None:
                continue
            for j in range(curr_num_cards, exchange[i]):
                self.exchange[j] = curr_num_coins
            curr_num_coins += 1
            curr_num_cards = exchange[i]
            if i > 0 and exchange[i-1] is None:
                curr_num_coins += 1
        self.exchange[curr_num_cards] = curr_num_coins
        self.max = curr_num_cards
        Card.cards.append(self)
        Card.name_to_card[self.name] = self

    def __getitem__(self, item): # HUHHHH???
        if not isinstance(item, int):
            raise TypeError("Can only harvest a integer number of beans")
        if item <= 0:
            return 0
        if item > self.max:
            return self.exchange[self.max]
        return self.exchange[item]

    def __str__(self):
        return self.name[:-5]

    def __repr__(self):
        return self.name[:-5]

    def pretty(self):
        def f(coins, n):
            if coins is None:
                return ''
            return '{}x: ${}'.format(n, coins)

        return '''
+----------+
|\033[1;3m{:^10}\033[0m|
|{:^10}|
|{:^10}|
|{:^10}|
|{:^10}|
|{:^10}|
+----------+
'''.format(self.name.split()[0],
           '{}x'.format(self.count),
           f(1, self._exchange[0]),
           f(2, self._exchange[1]),
           f(3, self._exchange[2]),
           f(4, self._exchange[3]),
           ).strip()


Card(name="Coffee Bean", exchange=(4, 7, 10, 12), count=24)
Card(name="Wax Bean", exchange=(4, 7, 9, 11), count=22)
Card(name="Blue Bean", exchange=(4, 6, 8, 10), count=20)
Card(name="Chili Bean", exchange=(3, 6, 8, 9), count=18)
Card(name="Stink Bean", exchange=(3, 5, 7, 8), count=16)
Card(name="Green Bean", exchange=(3, 5, 6, 7), count=14)
Card(name="Soy Bean", exchange=(2, 4, 6, 7), count=12)
Card(name="Black-eyed Bean", exchange=(2, 4, 5, 6), count=10)
Card(name="Red Bean", exchange=(2, 3, 4, 5), count=8)
Card(name="Garden Bean", exchange=(None, 2, 3, None), count=6)
Card(name="Cocoa Bean", exchange=(None, 2, 3, 4), count=4)
