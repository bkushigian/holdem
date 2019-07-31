from model import Model
from controller import Controller
from cli.view import ViewCLI
from state import *


class ControllerCLI(Controller):

    def __init__(self, model: Model, view: ViewCLI):
        self.model = model
        self.view = view
        #self.phase = view.game_state.phase     # is this OK? don't think I can, because game_state gets refreshed

    def process(self, cmd):

        self.model.game.error = None
        phase = self.view.game_state.phase

        cmd = cmd.split(maxsplit=2)     # but what if 2 spaces b/w first and second word?

        if cmd[0] == 'q':
            return False

        try:
            player = int(cmd[0]) - 1    # can declare player here?
        except ValueError:
            self.model.game.report_error(-1, 'invalid player number')   # ?
            #return True

        if player not in range(self.model.game.num_players):
            self.model.game.report_error(-1, 'invalid player number')  # ?
            # return True

        elif len(cmd) < 2:
            self.model.game.report_error(-1, 'invalid command')  # ?
            #return True

        else:
            action = cmd[1].lower()
            args = None

            if len(cmd) > 2:
                args = cmd[2]

            d = None    # need?

            if isinstance(self.view.game_state.phase, PhaseGameOver):   # should be updated when add actions to game over
                self.model.game.report_error(player, 'invalid action for game over')    # ?
                #

            elif action == 'harvest':
                if args and args.isdigit():
                    d = {'action': 'harvest', 'args': (player, int(args))}
                else:
                    self.model.game.report_error(player, 'invalid argument for harvest')  # ?
                    #return True

            elif player != self.model.game.curr_player:   # want to get curr_player from view instead? also, may want to change if add actions to phasegameover
                self.model.game.report_error(player, 'can only harvest if not your turn')  # ?
                #return True

            elif action == 'endphase':
                d = {'action': 'end_phase', 'args': None}

            elif isinstance(phase, PhaseI):
                if action == 'plant':
                    if args is None:
                        self.model.game.report_error(player, 'missing argument to plant')  # ?
                        #return True
                    else:
                        args = [arg.strip() for arg in args.split(',')]
                        try:
                            args = [int(arg) - 1 for arg in args]
                            d = {'action': 'plant', 'args': args}
                        except ValueError:
                            self.model.game.report_error(player, 'invalid argument to plant')  # ?
                            #return True

                else:
                    self.model.game.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                    #return True

            elif isinstance(phase, PhaseII):
                if action == 'plant':
                    d = {'action': 'plant', 'args': None}
                elif action == 'discard':
                    if args is None:
                        self.model.game.report_error(player, 'missing argument to discard')  # ?
                        #return True
                    else:
                        try:
                            args = int(args) - 1
                            d = {'action': 'plant', 'args': args}
                        except ValueError:
                            self.model.game.report_error(player, 'invalid argument to discard')  # ?
                            #return True

                else:
                    self.model.game.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                    #return True

            elif isinstance(phase, PhaseIII):
                if action == 'plant':
                    if args is None:
                        self.model.game.report_error(player, 'missing argument to plant')  # ?
                        #return True
                    else:
                        args = [arg.strip() for arg in args.split(',')]
                        try:
                            args = [int(arg) - 1 for arg in args]
                            d = {'action': 'plant', 'args': args}
                        except ValueError:
                            self.model.game.report_error(player, 'invalid argument to plant')  # ?
                            #return True

                elif action == 'draw':
                    d = {'action': 'draw', 'args': None}
                else:
                    self.model.game.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                    #return True

            elif isinstance(phase, PhaseIV):
                if action == 'draw':
                    d = {'action': 'draw', 'args': None}
                else:
                    self.model.game.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                    #return True

        if self.model.game.error is not None:

            d = {'action': None, 'args': None}

        self.model.update(**d)


        return True
