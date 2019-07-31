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

'''
    # added this for when the only update is an error. no longer recognizes kwargs
    def update(self):
        self.update_views()             # ???

'''
