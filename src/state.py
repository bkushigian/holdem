"""
All things statey
"""


class Player:
    def __init__(self, name):
        self.fields = [None, None, None]
        self.name = name
        self.coins = 0
        self.hand = []


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

    def __getitem__(self, item): # HUHHHH???
        if not isinstance(item, int):
            raise TypeError("Can only harvest a integer number of beans")
        if item <= 0:
            return 0
        if item > self.max:
            return self.exchange[self.max]
        return self.exchange[item]


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


class Game:
    def __init__(self, players):

        self.num_players = len(players)
        self.players = players  # List of players in order of turns
        self.deck = self.new_deck()
        self.discard = []
        self.offering = [None, None, None]
        self.curr_player = 0
        self.status = 0     # 0 = success, 1 = failure
        self.status_message = None

        self.phase = PhaseI(self)
        self.phase.create_phases()
        self.phase = self.phase.next    # WANT THIS? bc no phase1 first turn

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

        deck = [card for card in Card.cards for _ in range(card.count)
                if card.name != 'Garden Bean' and card.name != 'Cocoa Bean']
        r.shuffle(deck)
        return deck

    def game_over(self):
        # TODO: write game_over method
        pass

    def deal_to_player(self, player):
        if not self.deck:
            self.error(1, "Deal from empty deck")
            return False
        self.players[player].hand.insert(0, self.deck.pop())

    def error(self, status, msg):
        self.status = status
        self.status_message = msg


class Phase:
    def __init__(self, game):
        self.game = game
        self.next = None

    def update(self, **kwargs):
        pass

    def error(self, status, msg):
        self.game.error(status, msg)

    # want harvest method here?
    def harvest(self, args):
        if not isinstance(args, tuple) or len(args) != 2:
            self.error(1, 'wrong input')
            return

        p, f = args  # player, field indices
        if not isinstance(p, int) or not isinstance(f, int):
            self.error(1, 'wrong input')
            return

        if p not in range(self.game.num_players) or f not in range(len(self.game.players[p].fields)):
            self.error(1, 'wrong input')
            return

        player = self.game.players[p]
        field = player.fields[f]

        if field is None:
            return

        card, number = field
        coins = card[number]
        player.coins += coins
        self.game.discard.extend([card] * (number - coins))
        player.fields[f] = None


# want to discard all that are left
# have fixed offering list indices, with maybe None if have been planted
# assume want to plant all of something (have to change harvest to reflect that number may be > max?)
# want to add separate discard action in future?
class PhaseI(Phase):
    def __init__(self, game):
        super().__init__(game)

    def create_phases(self):
        self.next = PhaseII(self.game)

    def update(self, **kwargs):
        game = self.game
        self.error(0, '')

        action = kwargs['action']
        args = kwargs['args']

        if action == 'end_phase':
            for o in game.offering:
                if o is not None:
                    card, number = o    # is this wrong?
                    game.discard.extend([card] * number)
            game.offering = [None, None, None]
            game.phase = self.next

        elif action == 'harvest':   # implement bean protection rule?
            self.harvest(args)

        elif action == 'plant':
            if not isinstance(args, list) or any(arg not in range(len(game.offering)) for arg in args):
                self.error(1, 'wrong input')
                return
            for i in args:
                if game.offering[i] is None:
                    self.error(1, 'nothing at that offering index')
                    return
                card, number = game.offering[i]
                planting_field = None
                fields = game.players[game.curr_player].fields

                for j, f in enumerate(fields):
                    if planting_field is None and f is None:    # add comment?
                        planting_field = j
                    elif f is not None and f[0] == card:        # add comment?
                        planting_field = j
                if planting_field is None:
                    self.error(1, 'nowhere to plant: need to harvest first')
                    return
                if fields[planting_field] is None:
                    fields[planting_field] = (card, number)
                else:
                    fields[planting_field] = (card, fields[planting_field][1] + number)
                game.offering[i] = None

        else:
            self.error(1, 'invalid action')

class PhaseII(Phase):
    def __init__(self, game):
        super().__init__(game)
        self.next = PhaseIII(game)
        self.num_planted = 0
        self.done_discarding = False

    def end_phase(self):
        if self.num_planted < 1:
            self.error(1, 'need to plant at least one bean before ending phase')
            return
        self.num_planted = 0
        self.done_discarding = False

    def update(self, **kwargs):
        game = self.game
        self.error(0, '')

        action = kwargs['action']
        args = kwargs['args']

        if action == 'end_phase':
            self.end_phase()

        elif action == 'harvest':
            self.harvest(args)

        elif action == 'plant':
            if self.num_planted >= 2:
                self.error(1, 'already planted max number of beans')
                return
            if self.done_discarding:
                self.error(1, 'can\'t plant after discarding')
                return
            hand = game.players[game.curr_player].hand
            if not hand:
                self.error(1, 'no cards in hand to plant')
                return
            card = hand.pop()

            # modified from phase 1
            planting_field = None
            fields = game.players[game.curr_player].fields
            for j, f in enumerate(fields):
                if planting_field is None and f is None:    # add comment?
                    planting_field = j
                elif f is not None and f[0] == card:        # add comment?
                    planting_field = j
            if planting_field is None:
                self.error(1, 'nowhere to plant: need to harvest first')
                return
            if fields[planting_field] is None:
                fields[planting_field] = (card, 1)
            else:
                fields[planting_field] = (card, fields[planting_field][1] + 1)
            self.num_planted += 1

        elif action == 'discard':
            if self.num_planted < 1:
                self.error(1, 'need to plant at least one bean before discarding')
                return
            if self.done_discarding:
                self.error(1, 'can only discard once')
                return
            index = args
            hand = game.players[game.curr_player].hand
            if not isinstance(index, int) or index not in range(len(hand)):
                self.error(1, 'no card in that position in hand')
                return
            card = hand.pop(index)
            game.discard.append(card)
            self.done_discarding = True

        else:
            self.error(1, 'invalid action')


class PhaseIII(Phase):
    def __init__(self, game):
        super().__init__(game)
        self.next = PhaseIV(game)
        self.done_drawing = False

    def update(self, **kwargs):
        game = self.game
        self.error(0, '')

        action = kwargs['action']
        args = kwargs['args']

        if action == 'end_phase':
            if not self.done_drawing:
                self.error(1, 'must draw before ending phase')
                return
            self.done_drawing = False
            game.phase = self.next

        elif action == 'harvest':
            self.harvest(args)

        elif action == 'draw':
            if self.done_drawing:
                self.error(1, 'already drew')
                return
            for _ in range(3):
                if len(game.deck) > 0:          # change to if game.deck?
                    card = game.deck.pop()
                    index = None
                    for i, o in enumerate(game.offering):
                        if index is None and o is None:     # add comment?
                            index = i
                        if o is not None and o[0] == card:  # add comment?
                            index = i
                    if game.offering[index] is None:
                        game.offering[index] = (card, 1)
                    else:
                        game.offering[index] = (card, game.offering[index][1] + 1)
                else:
                    game.game_over()


            # TODO: Continue code review!!!!
            check_next_discard = True
            while check_next_discard:
                check_next_discard = False
                next_discard = game.discard[-1]
                for i in range(len(game.offering)):
                    # don't need to test check_next_discard below? trying to avoid adding to more than one pile, but maybe that wouldn't happen
                    if not check_next_discard and game.offering[i] is not None and game.offering[i][0] == next_discard:
                        game.offering[i] = (game.offering[i][0], game.offering[i][1] + 1)
                        game.discard.pop()
                        check_next_discard = True

            self.done_drawing = True

        elif action == 'plant':
            if not self.done_drawing:
                self.error(1, 'need to draw 3 first')
                return

            # copied from phase1
            if not isinstance(args, list) or any(arg not in range(len(game.offering)) for arg in args):
                self.error(1, 'wrong input')
                return
            for i in args:
                if game.offering[i] is None:
                    self.error(1, 'nothing at that offering index')
                    return
                card, number = game.offering[i]
                planting_field = None
                fields = game.players[game.curr_player].fields
                for j in range(len(fields)):
                    if planting_field is None and fields[j] is None:
                        planting_field = j
                    elif fields[j] is not None and fields[j][0] == card:
                        planting_field = j
                if planting_field is None:
                    self.error(1, 'nowhere to plant: need to harvest first')
                    return
                if fields[planting_field] is None:
                    fields[planting_field] = (card, number)
                else:
                    fields[planting_field] = (card, fields[planting_field][1] + number)
                game.offering[i] = None

        else:
            self.error(1, 'invalid action')


class PhaseIV(Phase):
    def __init__(self, game):
        super().__init__(game)  # added (). What about setting next?
        self.next = self.game.phase
        self.done_drawing = False

    def update(self, **kwargs):
        game = self.game
        self.error(0, '')

        action = kwargs['action']
        args = kwargs['args']

        if action == 'end_phase':
            if not self.done_drawing:
                self.error(1, 'need to draw before ending phase')
                return
            game.curr_player = (game.curr_player + 1) % game.num_players
            game.phase = self.next

        elif action == 'harvest':
            self.harvest(args)

        elif action == 'draw':
            if self.done_drawing:
                self.error(1, 'already drew')
                return
            for _ in range(2):
                if len(game.deck) > 0:  # if game.deck?
                    game.players[game.curr_player].insert(0, game.deck.pop())
                else:
                    game.game_over()

        else:
            self.error(1, 'invalid action')


class PhaseGameOver(Phase):
    def __init__(self, game):
        super().__init__(game)  # added (). What about setting next?
        self.next = None


    def update(self, **kwargs):
        self.error(0, '')   # want to use error method?

        # TODO: write update method
        if action == 'dummy':
            pass
        else:
            self.error(1, 'invalid action')