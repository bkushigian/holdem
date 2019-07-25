from cli.view import ViewCLI
from state import *

class Controller:

    def __init__(self, model, view):
        self.model = model
        self.view = view
        #self.phase = view.game_state.phase     # is this OK? don't think I can, because game_state gets refreshed

    def update_views(self):         # get rid of and call directly? from where?
        self.model.update_views()

    def process(self, cmd):
        if isinstance(self.view, ViewCLI):
            return self.process_cli(cmd)

    def process_cli(self, cmd):

        phase = self.view.game_state.phase

        cmd = cmd.split(maxsplit=2)     # but what if 2 spaces b/w first and second word?

        if cmd[0] == 'q':
            return False

        try:
            player = int(cmd[0]) - 1    # can declare player here?
            if player not in range(len(self.model.game.num_players)): # should check this?
                self.model.game.report_error(-1, 'invalid player number')   # ?
                return True
        except ValueError:
            self.model.game.report_error(-1, 'invalid player number')   # ?
            return True

        if len(cmd) < 2:
            self.model.game.report_error(-1, 'invalid command')  # ?
            return True

        action = cmd[1].lower()
        args = None

        if len(cmd) > 2:
            args = cmd[2:]

        d = None

        if isinstance(self.view.game_state.phase, PhaseGameOver):   # should be updated when add actions to game over
            self.model.game.report_error(player, 'invalid action for game over')    # ?
            return True

        elif action == 'harvest':
            if args and args.isdigit():
                d = {'action': 'harvest', 'args': (player, args)}
            else:
                self.model.game.report_error(player, 'invalid argument for harvest')  # ?
                return True

        elif player != self.model.game.curr_player:   # want to get curr_player from view instead? also, may want to change if add actions to phasegameover
            self.model.game.report_error(player, 'can only harvest if not your turn')  # ?
            return True

        elif action == 'endphase':
            d = {'action': 'end_phase', 'args': None}

        elif isinstance(phase, PhaseI):
            if action == 'plant':
                if args is None:
                    self.model.game.report_error(player, 'missing argument to plant')  # ?
                    return True
                args = [arg.strip() for arg in args.split(',')]
                try:
                    args = [int(arg) - 1 for arg in args]
                except ValueError:
                    self.model.game.report_error(player, 'invalid argument to plant')  # ?
                    return True
                d = {'action': 'plant', 'args': args}
            else:
                self.model.game.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                return True

        elif isinstance(phase, PhaseII):
            if action == 'plant':
                d = {'action': 'plant', 'args': None}
            elif action == 'discard':
                if args is None:
                    self.model.game.report_error(player, 'missing argument to discard')  # ?
                    return True
                try:
                    args = int(args) - 1
                except ValueError:
                    self.model.game.report_error(player, 'invalid argument to discard')  # ?
                    return True
                d = {'action': 'plant', 'args': args}
            else:
                self.model.game.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                return True

        elif isinstance(phase, PhaseIII):
            if action == 'plant':
                if args is None:
                    self.model.game.report_error(player, 'missing argument to plant')  # ?
                    return True
                args = [arg.strip() for arg in args.split(',')]
                try:
                    args = [int(arg) - 1 for arg in args]
                except ValueError:
                    self.model.game.report_error(player, 'invalid argument to plant')  # ?
                    return True
                d = {'action': 'plant', 'args': args}
            elif action == 'draw':
                d = {'action': 'draw', 'args': None}
            else:
                self.model.game.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                return True

        elif isinstance(phase, PhaseIV):
            if action == 'draw':
                d = {'action': 'draw', 'args': None}
            else:
                self.model.game.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                return True

        self.model.phase.update(**d)    # ???
        return True
