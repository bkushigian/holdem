from state import *
from model import Model
from view import *
from cli.view import ViewCLI
from cli.controller import ControllerCLI


def main():

    p1 = input('Player 1 name: ')
    p2 = input('Player 2 name: ')

    game = Game([Player(p1), Player(p2)])
    model = Model(game)

    for i in range(len(game.players)):
        model.register_view(ViewCLI(ViewGameState.from_game(game, i)))

    controller = ControllerCLI(model, model.views[0])   # ??? Don't know what else to do

    while True:
        cmd = input('>>>')
        cont = controller.process(cmd)
        for view in model.views:
            view.render()
        if not cont:
            break


if __name__ == '__main__': main()