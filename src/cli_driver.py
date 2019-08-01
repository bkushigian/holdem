from sys import argv, exit
from state import *
from model import Model
from view import *
from cli.view import ViewCLI
from cli.controller import ControllerCLI


def main():
    if len(argv) != 3:
        print("usage: python cli_driver.py <player1> <player2>")
        exit(1)
    _, p1, p2 = argv

    game = Game([Player(p1), Player(p2)])
    model = Model(game)

    for i in range(game.num_players):
        model.register_view(ViewCLI(ViewGameState.from_game(game, i)))

    controller = ControllerCLI(model, model.views[0])   # ??? Don't know what else to do

    cont = True
    while cont:
        # for view in model.views[:game.curr_player] + model.views[game.curr_player + 1:]:
        #     view.render()
        model.views[game.curr_player].render()    # Render current player last
        cmd = input('\033[1mEnter\033[0m <action> [args...]\n\033[{};1m({}) >>>\033[0m '.format(
            model.views[game.curr_player].formatter.player_colors[game.curr_player],
            game.players[game.curr_player].name))
        cont = controller.process(cmd)


if __name__ == '__main__': main()