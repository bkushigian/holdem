from action import ActionHarvest, ActionPlantFromOffering


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