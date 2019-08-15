from controller import Controller
from state import PhaseGameOver, PhaseI, PhaseII, PhaseIII, PhaseIV


class ClientControllerCLI(Controller):

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.view = client.view   # TODO: Remove reference to view, use client instead
        self.possible_actions = ['harvest', 'plant', 'next', 'draw']

    def report_error(self, code, msg):
        return {'type': 'error', 'code': code, 'msg': msg}

    def process(self, cmd):
        d = {'action': None, 'args': ()}
        # self.model.set_error(None)

        phase = self.view.game_state.phase
        if not cmd.strip():
            return {'type': 'empty', 'data': None}

        cmd = cmd.split(maxsplit=2)     # but what if 2 spaces b/w first and second word?

        if cmd[0] == 'q':
            d['action'] = 'quit'
            return {'type': 'game-action', 'data': d}

        elif len(cmd) < 1:
            return self.report_error(-1, 'invalid command')

        else:
            action = cmd[0].lower()
            args = None

            if len(cmd) > 1:
                args = cmd[1]

            if isinstance(self.view.game_state.phase, PhaseGameOver):
                return self.report_error(1, 'invalid action for game over')

            elif action.lower() in ('harvest', 'h'):
                if args and args.isdigit():
                    d = {'action': 'harvest', 'args': (self.client.game_state.owner,  int(args) - 1)}
                else:
                    return self.report_error(1, 'invalid argument for harvest')

            elif action.lower() in ('next', 'n'):
                d = {'action': 'next', 'args': ()}

            elif action.lower() in ('undo', 'u'):
                d = {'action': 'undo', 'args': None}

            elif isinstance(phase, PhaseI):
                if action.lower() in ('plant', 'p'):
                    if args is None:
                        return self.report_error(1, 'missing argument to plant')
                    args = [arg.strip() for arg in args.split(',')]
                    try:
                        args = [int(arg) - 1 for arg in args]
                        d = {'action': 'plant', 'args': args}
                    except ValueError:
                        return self.report_error(1, 'invalid argument to plant')
                elif action.lower() in ('next', 'n'):
                    d = {'action': action, 'args': None}

                else:
                    return self.report_error(1, 'invalid action for Phase {}'.format(phase))  # ?

            elif isinstance(phase, PhaseII):
                if action.lower() in ('plant', 'p'):
                    d = {'action': 'plant', 'args': None}
                elif action.lower() in ('discard', 'd'):
                    if args is None:
                        return self.report_error(1, 'missing argument to discard')
                    else:
                        try:
                            d = {'action': 'discard', 'args': int(args) - 1}
                        except ValueError:
                            return self.report_error(1, 'invalid argument to discard')

                elif action.lower() in ('next', 'n'):
                    d = {'action': action, 'args': None}
                else:
                    return self.report_error(1, 'invalid action for Phase {}'.format(phase))  # ?

            elif isinstance(phase, PhaseIII):
                if action.lower() in ('plant', 'p'):
                    if args is None:
                        return self.report_error(1, 'missing argument to plant')
                    else:
                        args = [arg.strip() for arg in args.split(',')]
                        try:
                            d = {'action': 'plant', 'args': [int(arg) - 1 for arg in args]}
                        except ValueError:
                            return self.report_error(1, 'invalid argument to plant')

                elif action.lower() in ('draw', 'd'):
                    d = {'action': 'draw', 'args': None}
                elif action.lower() in ('next', 'n'):
                    d = {'action': action, 'args': None}
                else:
                    return self.report_error(1, 'invalid action for Phase {}'.format(phase))

            elif isinstance(phase, PhaseIV):
                if action.lower() in ('draw', 'd'):
                    d = {'action': 'draw', 'args': None}
                elif action.lower() in ('next', 'n'):
                    d = {'action': action, 'args': None}
                else:
                    return self.report_error(1, 'invalid action for Phase {}'.format(phase))

        return {'type': 'game-action', 'data': d}
