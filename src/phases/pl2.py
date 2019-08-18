from action import ActionEndPhaseI, ActionPlantPhaseII, ActionDiscard
from phases.phase import Phase


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