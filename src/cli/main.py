from sys import argv
from state import Player, Card, Game
from cli.view import ViewCLI


def main():
    p1, p2 = argv[1:2]
    p1 = Player(p1)
    p2 = Player(p2)
    v = ViewCLI()



if __name__ == '__main__':
    main()
