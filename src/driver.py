from controller import Controller
from state import *
from model import Model

def main():

    p1 = input('Player 1 name: ')
    p2 = input('Player 2 name: ')
    game = Game([p1, p2])
    model = Model(game)
    controller = Controller(model)

    while True:
        cmd = input('>>>')
        cont = controller.process(cmd)
        if not cont:
            break








if __name__ == '__main__': main()