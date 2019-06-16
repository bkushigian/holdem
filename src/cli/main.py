from sys import argv
from state import Player, Card, Game
from cli.view import ViewCLI

def Model:
    def __init__(self, players):
       self.game_state = Game(players) 
       self.views = {}

    def register_view(self, player, view):
        self.views[player] = view

    def update(self, **kwargs):
        # TODO: Update game state, pass result to views
        self.game_state.update(kwargs)
        pass

def main():
    p1, p2 = argv[1:2]
    p1 = Player(p1)
    p2 = Player(p2)
    m = Model([p1,p2])
    v = ViewCLI()



if __name__ == '__main__':
    main()
