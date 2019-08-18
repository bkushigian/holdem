from model import Model
from controller import Controller
from cli.view import ViewCLI
from phases import pl2


class ControllerCLI(Controller):

    def __init__(self, model: Model, view: ViewCLI):
        self.model = model
        self.view = view
        self.possible_actions = ['harvest', 'plant', 'next', 'draw']
        #self.phase = view.game_state.phase     # is this OK? don't think I can, because game_state gets refreshed

    def process(self, cmd):
        self.model.set_error(None)
        phase = self.view.game_state.phase
        if not cmd.strip():
            return True

        cmd = cmd.split(maxsplit=2)     # but what if 2 spaces b/w first and second word?

        if cmd[0] == 'q':
            return False

        # try:
        #     player = int(cmd[0]) - 1    # can declare player here?
        # except ValueError:
        #     self.model.report_error(-1, 'invalid player number')   # ?
        #     return True

        player = self.model.current_player()

        cmd = [player] + cmd  # XXX: This is a hack!!! This conforms with the player including their player number

        if player not in range(self.model.get_num_players()):
            self.model.report_error(-1, 'invalid player number')  # ?
            return True

        elif len(cmd) < 2:
            self.model.report_error(-1, 'invalid command')  # ?
            return True

        else:
            action = cmd[1].lower()
            args = None

            if len(cmd) > 2:
                args = cmd[2]

            d = None    # need?

            if isinstance(self.view.game_state.phase, pl2.PhaseGameOver):   # should be updated when add actions to game over
                self.model.report_error(player, 'invalid action for game over')    # ?
                return True

            elif action.lower() in ('harvest', 'h'):
                if args and args.isdigit():
                    d = {'action': 'harvest', 'args': (player, int(args) - 1)}
                else:
                    self.model.report_error(player, 'invalid argument for harvest')  # ?
                    return True

            elif player != self.model.current_player():   # want to get curr_player from view instead? also, may want to change if add actions to phasegameover
                self.model.report_error(player, 'can only harvest if not your turn')  # ?
                return True

            elif action.lower() in ('next', 'n'):
                d = {'action': 'next', 'args': None}

            elif action.lower() in ('undo', 'u'):
                d = {'action': 'undo', 'args': None}

            elif isinstance(phase, pl2.PhaseI):
                if action.lower() in ('plant', 'p'):
                    if args is None:
                        self.model.report_error(player, 'missing argument to plant')  # ?
                        return True
                    else:
                        args = [arg.strip() for arg in args.split(',')]
                        try:
                            args = [int(arg) - 1 for arg in args]
                            d = {'action': 'plant', 'args': args}
                        except ValueError:
                            self.model.report_error(player, 'invalid argument to plant')  # ?
                            return True
                elif action.lower() in ('next', 'n'):
                    d = {'action': action, 'args': None}

                else:
                    self.model.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                    return True

            elif isinstance(phase, pl2.PhaseII):
                if action.lower() in ('plant', 'p'):
                    d = {'action': 'plant', 'args': None}
                elif action.lower() in ('discard', 'd'):
                    if args is None:
                        self.model.report_error(player, 'missing argument to discard')  # ?
                        return True
                    else:
                        try:
                            args = int(args) - 1
                            d = {'action': 'discard', 'args': args}
                        except ValueError:
                            self.model.report_error(player, 'invalid argument to discard')  # ?
                            return True

                elif action.lower() in ('next', 'n'):
                    d = {'action': action, 'args': None}
                else:
                    self.model.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                    return True

            elif isinstance(phase, pl2.PhaseIII):
                if action.lower() in ('plant', 'p'):
                    if args is None:
                        self.model.report_error(player, 'missing argument to plant')  # ?
                        return True
                    else:
                        args = [arg.strip() for arg in args.split(',')]
                        try:
                            args = [int(arg) - 1 for arg in args]
                            d = {'action': 'plant', 'args': args}
                        except ValueError:
                            self.model.report_error(player, 'invalid argument to plant')  # ?
                            return True

                elif action.lower() in ('draw', 'd'):
                    d = {'action': 'draw', 'args': None}
                elif action.lower() in ('next', 'n'):
                    d = {'action': action, 'args': None}
                else:
                    self.model.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                    return True

            elif isinstance(phase, pl2.PhaseIV):
                if action.lower() in ('draw', 'd'):
                    d = {'action': 'draw', 'args': None}
                elif action.lower() in ('next', 'n'):
                    d = {'action': action, 'args': None}
                else:
                    self.model.report_error(player, 'invalid action for Phase {}'.format(phase))  # ?
                    return True

        self.model.update(**d)

        return True
