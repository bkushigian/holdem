from sys import argv
from game import Player, Game
from cards import Card
from cli.view import ViewCLI


def main():
    p1, p2 = argv[1:2]
    p1 = Player(p1)
    p2 = Player(p2)
    v = ViewCLI()



if __name__ == '__main__':
    main()
