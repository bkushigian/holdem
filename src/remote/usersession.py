from model import Model
from remote.states import UserSessionState as State
from state import Game


class UserSession:
    _id = -1

    def __init__(self, conn, addr, network_manager, username=None):
        print("Creating user session")
        self.conn = conn
        self.addr = addr
        self.nm = network_manager
        self.username = username
        self.state = State.NEW

        self.sid = UserSession._new_id()
        self.game: Model = None
        self.on_exit = []           # A list of callables to call on exit

        self.outb = b''       # outgoing message
        self.recv = []        # Recieved messages

    def close(self):
        for f in self.on_exit:
            f()
        if self.conn:
            self.conn.close()

    def handle(self, msg: bytes):
        """
        Handle an incoming message
        :param msg: unpacked message
        :return:
        """
        self.recv.append(msg)

        if not isinstance(msg, dict) or "type" not in msg:
            raise ValueError("msg must be an unpacked message of the form {\"type\": tp, ...}")

        tp = msg['type']
        data = msg.get('data')

        state = self.state

        print("handle()---sid:{} tp:{} data: {} state: {}".format(self.sid, tp, data, state))
        if state == State.NEW:
            if tp != "session-initialization":
                self.mark_illegal_state(state, tp, "expected message of type 'session-initialization'")
            self.outb += self.nm.pack({'type': 'session-initialization-reply',
                                       'data': {'status': 'success',
                                                'sid': self.sid,
                                                'key': None}})
            self.state = State.SENT_SESSION_DATA
        elif state == State.SENT_SESSION_DATA:
            if tp != 'greeting':
                self.mark_illegal_state(state, tp, "expected message of type 'greeting'")
            elif not data:
                self.mark_illegal_state(state, tp, "greeting must supply a data field: {'username': name}")
            else:
                name = data['username']
                if name is None:
                    reply_data = self.nm.namegen.generate_session_username(self)
                else:
                    reply_data = self.nm.namegen.request_session_username(self, name)
                self.outb += self.nm.pack({'type': 'greeting-reply', 'data': reply_data})
                if reply_data['status'] == 'success':
                    self.state = State.FRESH
                else:
                    # Technically not necessary, but we make it explicit
                    self.state = State.NEW

        elif state == State.FRESH:
            if tp != 'new-game-request':
                self.mark_illegal_state(state, tp, "expected message of type 'new-game-request'")
            self.state = State.GAME_QUEUE
            self.nm.add_to_new_game_queue(self.sid)
            print('adding to game queue', self.sid)

        elif state == State.GAME_QUEUE:
            pass

        elif state == State.GAME:
            if tp != 'game-action':
                self.mark_illegal_state(state, tp, "expected message of type 'game-action'")
            self.game.update(**data)

    def mark_illegal_state(self, state, tp, message=''):
        raise ValueError("In state {}: cannot transfer on {}{}".format(
            state, tp, ': ' + message if message else '.'))

    def start_game(self, game: Model):
        if self.state is not State.GAME_QUEUE:
            raise RuntimeError("Cannot start a game while not in waiting state!!!", self.state)
        self.game = game
        self.state = State.GAME

    @staticmethod
    def _new_id():
        UserSession._id += 1
        return UserSession._id


