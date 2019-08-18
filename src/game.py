"""
All things statey
"""
from action import Action, ActionHarvest, ActionEndPhaseI, ActionPlantFromOffering, ActionPlantPhaseII, ActionDiscard
from cards import Card


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


class Phase:
    def __init__(self, game):
        self.game = game
        self.next = None

    def start_phase(self):
        pass

    def end_phase(self):
        self.game.phase = self.next
        self.game.phase.start_phase()

    def update(self, **kwargs):
        pass

    def number(self):
        pass

    def get_valid_actions(self):
        raise NotImplementedError("Phase.get_valid_actions is abstract")

    '''
    def error(self, status, msg):
        self.game.error(status, msg)
    '''

    def report_error(self, player, msg):
        self.game.report_error(player, msg)

    def undo(self):
        if not self.game.actions:
            self.report_error(self.game.curr_player, 'can\'t undo')
            return
        action = self.game.actions.pop()
        action.inverse()

    # want harvest method here?
    def harvest(self, args):
        if not isinstance(args, tuple) or len(args) != 2:
            # controller will obviate need for this, but -1 for now
            self.report_error(-1, 'harvest: bad input: argument should be a length-2 tuple (player-index, field-index)')
            return

        player_idx, field_idx = args  # player, field indices
        if not isinstance(player_idx, int) or player_idx not in range(self.game.num_players):
            # hopefully not needed in future, but -1 for now
            self.report_error(-1, 'harvest:  bad input: player index {} is not a valid integer in range <0..{}>'.format(
                player_idx, self.game.num_players - 1))
            return

        if not isinstance(field_idx, int) or field_idx not in range(len(self.game.players[player_idx].fields)):
            self.report_error(player_idx, 'harvest: bad input: field index {} is not a valid integer in range <0..{}>'
                              .format(field_idx, len(self.game.players[player_idx].fields) - 1))
            return

        player = self.game.players[player_idx]
        field = player.fields[field_idx]

        if field is None:
            return

        card, number = field
        coins = card[number]
        player.coins += coins
        self.game.discard.extend([card] * (number - coins))
        player.fields[field_idx] = None

        self.game.actions.append(ActionHarvest(self.game, player_idx, field_idx, card, number, coins))

    def plant_from_offering(self, idxs):
        game = self.game
        fields = game.players[game.curr_player].fields

        open_fields = 0
        matches = 0

        for i in idxs:
            if game.offering[i] is None:
                self.report_error(self.game.curr_player, 'nothing at offering index {}'.format(i+1))
                return
        cards = [game.offering[i][0] for i in idxs]
        for f in fields:
            if f is None:
                open_fields += 1
            elif f[0] in cards:
                matches += 1
        if matches + open_fields < len(idxs):
            self.report_error(self.game.curr_player, 'nowhere to plant: need to harvest first')
            return

        action_info_list = []

        for i in idxs:
            card, number = game.offering[i]
            planting_field = None

            for j, f in enumerate(fields):
                # If haven't found a place to plant yet and field is empty, pick this field but keep looking
                if planting_field is None and f is None:
                    planting_field = j
                # If field contains same bean type, pick this field
                elif f is not None and f[0] == card:
                    planting_field = j
                    break

            if fields[planting_field] is None:
                fields[planting_field] = (card, number)
            else:
                fields[planting_field] = (card, fields[planting_field][1] + number)
            game.offering[i] = None

            action_info_list.append((i, card, number, planting_field))

        game.actions.append(ActionPlantFromOffering(self.game, self.game.curr_player, action_info_list))


class TwoPlayerPhases:
    class PhaseI(Phase):
        def get_valid_actions(self):

            actions = ['harvest']
            if self.game.offering:
                if len(self.game.offering) == 1:
                    actions.append('plant 0'.format(len(self.game.offering) - 1))   # ???
                else:
                    actions.append('plant from offering <1..{}>'.format(len(self.game.offering)))
            if self.game.actions:
                actions.append('undo')
            actions.append('next')
            return actions

        def __init__(self, game):
            super().__init__(game)

        def create_phases(self):
            self.next = TwoPlayerPhases.PhaseII(self.game)

        def end_phase(self):
            offering_copy = self.game.offering.copy()
            num = 0
            for o in self.game.offering:
                if o is not None:
                    card, number = o
                    self.game.discard.extend([card] * number)
                    num += number
            self.game.offering = [None, None, None]

            self.game.actions.append(ActionEndPhaseI(self.game, self.game.curr_player, offering_copy, num))  # needs to be before super in phase 4 because curr_player changes at end of phase

            super().end_phase()

        def update(self, **kwargs):
            game = self.game
            # self.game.error = None     # resetting somewhere else now...  but that sounds bad

            action = kwargs['action']
            args = kwargs['args']

            if action is None:
                return

            elif action == 'undo':
                self.undo()

            # At end of phase, discard all of offering that hasn't been planted
            elif action == 'next':
                self.end_phase()

            elif action == 'harvest':   # implement bean protection rule?
                self.harvest(args)

            # Plant from offering into field
            elif action == 'plant':
                if not isinstance(args, list) or any(arg not in range(len(game.offering)) for arg in args):
                    self.report_error(self.game.curr_player, 'wrong input')
                    return
                self.plant_from_offering(args)

            else:
                self.report_error(self.game.curr_player, 'invalid action')

        def number(self):
            return 1

        def __str__(self):
            return '1'

    class PhaseII(Phase):
        def __init__(self, game):
            super().__init__(game)
            self.next = TwoPlayerPhases.PhaseIII(game)
            self.num_planted = 0
            self.done_discarding = False

        def get_valid_actions(self):
            actions = ['harvest']  # ['discard', 'next']
            cards_in_hand = len(self.game.players[self.game.curr_player].hand)

            if self.num_planted <= 1 and cards_in_hand and not self.done_discarding:
                actions.append('plant')

            if self.num_planted >= 1 and cards_in_hand and not self.done_discarding:
                actions.append('discard')

            if self.game.actions:
                actions.append('undo')

            if self.num_planted >= 1:
                actions.append('next')
            return actions

        def end_phase(self):
            if self.num_planted < 1:
                self.report_error(self.game.curr_player, 'need to plant at least one bean before ending phase')
                return
            self.num_planted = 0
            self.done_discarding = False
            super().end_phase()

        def update(self, **kwargs):
            game = self.game
            #self.error(0, '')
            #self.game.error = None

            action = kwargs['action']
            args = kwargs['args']

            if action is None:
                return

            elif action == 'undo':
                self.undo()

            elif action == 'next':
                self.end_phase()

            elif action == 'harvest':
                self.harvest(args)

            # Plant from hand to field
            elif action == 'plant':
                if self.num_planted >= 2:
                    self.report_error(game.curr_player, 'already planted max number of beans')
                    return
                if self.done_discarding:
                    self.report_error(game.curr_player, 'can\'t plant after discarding')
                    return
                hand = game.players[game.curr_player].hand
                if not hand:
                    self.report_error(game.curr_player, 'no cards in hand to plant')
                    return
                card = hand[-1]

                # modified from phase 1

                planting_field = None
                fields = game.players[game.curr_player].fields
                for j, f in enumerate(fields):
                    # If haven't found a place to plant yet and field is empty, pick this field but keep looking
                    if planting_field is None and f is None:
                        planting_field = j
                    # If field contains same bean type, pick this field
                    elif f is not None and f[0] == card:
                        planting_field = j
                        break
                if planting_field is None:
                    self.report_error(game.curr_player, 'nowhere to plant: need to harvest first')
                    return
                hand.pop()
                if fields[planting_field] is None:
                    fields[planting_field] = (card, 1)
                else:
                    fields[planting_field] = (card, fields[planting_field][1] + 1)
                self.num_planted += 1

                self.game.actions.append(ActionPlantPhaseII(game, game.curr_player, card, planting_field))

            # Discard from hand
            elif action == 'discard':
                if self.num_planted < 1:
                    self.report_error(game.curr_player, 'need to plant at least one bean before discarding')
                    return
                if self.done_discarding:
                    self.report_error(game.curr_player, 'can only discard once')
                    return
                index = args
                hand = game.players[game.curr_player].hand
                if not isinstance(index, int) or index not in range(len(hand)):
                    self.report_error(game.curr_player, 'no card in that position in hand')
                    return
                card = hand.pop(index)
                game.discard.append(card)
                self.done_discarding = True
                game.actions.append(ActionDiscard(game, game.curr_player, index))

            else:
                self.report_error(game.curr_player, 'invalid action')

        def number(self):
            return 2

        def __str__(self):
            return '2'


    class PhaseIII(Phase):
        def __init__(self, game):
            super().__init__(game)
            self.next = TwoPlayerPhases.PhaseIV(game)
            self.game_over = False      # move to game?

        def get_valid_actions(self):
            actions = ['harvest']

            if any(self.game.offering):
                actions.append('plant')

            if self.game.actions:
                actions.append('undo')

            actions.append('next')
            return actions

        def end_phase(self):
            if self.game_over:
                self.game.game_over()
                self.game.actions = []       # being lazy. could make game_over undo-able?
                return
            super().end_phase()

        def start_phase(self):
            game = self.game
            # Draw from deck into offering
            for _ in range(3):
                if game.deck:
                    card = game.deck.pop()
                    index = None
                    for i, o in enumerate(game.offering):
                        # If haven't found a place to put card and this spot is empty, pick this spot but keep looking
                        if index is None and o is None:
                            index = i
                        # If this spot contains same bean type, pick this spot
                        if o is not None and o[0] == card:
                            index = i
                            break
                    if game.offering[index] is None:
                        game.offering[index] = (card, 1)
                    else:
                        game.offering[index] = (card, game.offering[index][1] + 1)
                else:
                    # Stop drawing, but can continue planting, etc., until end of phase
                    self.game_over = True
                    break

            # While the top card in discard pile matches a card in the offering, add it to the offering.
            check_next_discard = True   # True while want to continue checking the top card in discard pile
            while check_next_discard:
                if not game.discard:
                    break
                check_next_discard = False
                next_discard = game.discard[-1]
                for i, o in enumerate(game.offering):
                    # don't need to test check_next_discard below? trying to avoid adding to more than one pile, but maybe that wouldn't happen
                    if not check_next_discard and o is not None and o[0] == next_discard:
                        game.offering[i] = (o[0], o[1] + 1)
                        game.discard.pop()
                        check_next_discard = True

            game.actions = []   # ???

        def update(self, **kwargs):
            game = self.game
            # self.game.error = None

            action = kwargs['action']
            args = kwargs['args']

            if action is None:
                return

            elif action == 'undo':
                self.undo()

            elif action == 'next':
                self.end_phase()

            elif action == 'harvest':
                self.harvest(args)

            # Plant from offering into field
            elif action == 'plant':
                if not isinstance(args, list) or any(arg not in range(len(game.offering)) for arg in args):
                    self.report_error(game.curr_player, 'wrong input')
                    return
                self.plant_from_offering(args)

            else:
                self.report_error(game.curr_player, 'invalid action')

        def number(self):
            return 3

        def __str__(self):
            return '3'

    class PhaseIV(Phase):
        def __init__(self, game):
            super().__init__(game)
            self.next = self.game.phase

        def get_valid_actions(self):
            return ['harvest', 'next']

        def start_phase(self):
            game = self.game
            for _ in range(2):
                if game.deck:
                    game.players[game.curr_player].hand.insert(0, game.deck.pop())

                else:
                    game.game_over()    # ??? does this get screwed up b/c in for loop?
                    break               # added break due to above
            game.actions = []

        def end_phase(self):
            self.game.curr_player = (self.game.curr_player + 1) % self.game.num_players
            super().end_phase()

        def update(self, **kwargs):
            game = self.game

            action = kwargs['action']
            args = kwargs['args']

            if action is None:
                return

            elif action == 'next':
                self.end_phase()

            elif action == 'harvest':
                self.harvest(args)

            else:
                self.report_error(game.curr_player, 'invalid action')

        def number(self):
            return 4

        def __str__(self):
            return '4'


    class PhaseGameOver(Phase):
        def __init__(self, game):
            super().__init__(game)
            self.next = None

        def get_valid_actions(self):
            return []

        def update(self, **kwargs):
            # self.game.error = None

            # TODO: write update method

            action = kwargs['action']
            args = kwargs['args']

            if action is None:
                return

            elif action == 'dummy':
                pass

            else:
                self.report_error(self.game.curr_player, 'invalid action')

        def number(self):
            return 5        # ???

        def __str__(self):
            return 'Game Over'


class State:
    def __init__(self, name=None):
        self.actions = []
        self.name = name

    def add_action(self, name, target, desc=''):
        self.actions.append(Action(name, target, desc))


class StateMachine:

    def __init__(self, names, actions):
        self.actions_matrix = actions
        self.states = [State(name) for name in names]
        for i, row in enumerate(self.states):
            for j, (action, desc) in enumerate(self.states):
                self.states[i].add_action(action, self.states[j], desc=desc)
        self.current_action = None

    def reset(self):
        pass

    def get_states(self):
        raise NotImplementedError('StateMachine.get_states is abstract')

    def get_current_state(self):
        raise NotImplementedError('StateMachine.get_current_state is abstract')

    def get_available_actions(self):
        raise NotImplementedError('StateMachine.get_available_actions is abstract')

    def take_action(self, action, *args):
        raise NotImplementedError('StateMachine.take_action is abstract')
