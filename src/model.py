from view import (ViewServerMixin, ViewClientMixin,
         ViewGameState, ViewPlayer)
from cli.view import ViewCLI

class Model:
    def __init__(self, game):
        self.game = game
        self.views = []
        for i in range(len(game.players)):
            self.register_view(ViewCLI(ViewGameState.from_game(game, i)))

    def register_view(self, view_server_mixin):
        self.views.append(view_server_mixin)

    def update_views(self):
        for i, view in enumerate(self.views):
            view.update(ViewGameState.from_game(self.game, i))

