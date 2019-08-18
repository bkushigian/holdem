class Action:
    def __init__(self, game, player):
        self.game = game
        self.player = player

    def inverse(self):
        pass


class ActionHarvest(Action):
    def __init__(self, game, player, field, card, number, coins):
        """
        :param game: game reference
        :param player: index
        :param field: index
        :param card: card reference
        :param number: total number harvested
        :param coins: number converted to coins
        """
        super().__init__(game, player)
        self.field = field
        self.card = card
        self.number = number
        self.coins = coins

    def inverse(self):
        self.game.discard = self.game.discard[:-(self.number - self.coins)]
        self.game.players[self.player].coins -= self.coins
        self.game.players[self.player].fields[self.field] = (self.card, self.number)


class ActionEndPhaseI(Action):

    def __init__(self, game, player, offering, number):
        """
        :param game: game reference
        :param player: index
        :param offering: list of tuples for the offering before end of phase
        :param number: total number of cards that went to discard
        """
        super().__init__(game, player)
        self.offering = offering
        self.number = number

    def inverse(self):
        self.game.phase = self.game.phase.next.next.next    # go back to phase 1
        self.game.offering = self.offering
        self.game.discard = self.game.discard[:-self.number]


class ActionPlantFromOffering(Action):

    def __init__(self, game, player, index_list):
        """
        :param game: game reference
        :param player: index
        :param index_list: list of (offering_index, card_reference, number, field_index)
        """
        super().__init__(game, player)
        self.index_list = index_list

    def inverse(self):
        for off_index, card, number, field_index in self.index_list:
            fields = self.game.players[self.player].fields
            fields[field_index] = (fields[field_index][0], fields[field_index][1] - number)
            if fields[field_index][1] == 0:
                fields[field_index] = None
            self.game.offering[off_index] = (card, number)


class ActionPlantPhaseII(Action):
    def __init__(self, game, player, card, field):
        """
        :param game: game reference
        :param player: index
        :param card: card ref
        :param field: field index
        """
        super().__init__(game, player)
        self.card = card
        self.field = field

    def inverse(self):
        fields = self.game.players[self.player].fields
        fields[self.field] = (fields[self.field][0], fields[self.field][1] - 1)
        if fields[self.field][1] == 0:
            fields[self.field] = None
        self.game.players[self.player].hand.append(self.card)
        self.game.phase.num_planted -= 1


class ActionDiscard(Action):
    def __init__(self, game, player, index):
        """
        :param game: game reference
        :param player: player index
        :param index: index of card in hand before discard
        """
        super().__init__(game, player)
        self.index = index

    def inverse(self):
        card = self.game.discard.pop()
        self.game.players[self.player].hand.insert(self.index, card)
        self.game.phase.done_discarding = False