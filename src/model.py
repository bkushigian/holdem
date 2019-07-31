from view import ViewGameState


class Model:
    def __init__(self, game):
        self.game = game
        self.views = []

    def register_view(self, view_server_mixin):
        self.views.append(view_server_mixin)

    def update_views(self):
        for i, view in enumerate(self.views):
            view.update(ViewGameState.from_game(self.game, i))

    def update(self, **kwargs):
        self.game.phase.update(**kwargs)
        self.update_views()             # ???

    def report_error(self, player, msg):
        self.game.report_error(player, msg)
        self.update_views()

    def current_player(self):
        return self.game.curr_player

    def get_error(self):
        return self.game.error

    def set_error(self, error):
        self.game.error = error

    def get_num_players(self):
        return self.game.num_players
