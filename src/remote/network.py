import pickle

from remote.usersession import UserSession
import remote.namegen
from typing import Dict, Optional, List
from types import SimpleNamespace
from model import Model
from remote.view import ServerView

from state import Player, Game
from view import ViewGameState

HEADERSIZE = 16
sid_t = int        # A typing alias


def pack(msg):
    msg = pickle.dumps(msg)
    msg = bytes(_make_header(len(msg)), 'utf-8') + msg
    return msg


def unpack(msg):
    header, msg = _get_header(msg)
    size = int(header)
    if size != len(msg):
        raise PacketFormatError("Error with message size: {} vs {}".format(size, len(msg)))
    return pickle.loads(msg)


def _make_header(length):

    header = '{{:<{}}}'.format(HEADERSIZE).format(length)
    return header


def _get_header(msg):
    if len(msg) < HEADERSIZE:
        return None
    return msg[:HEADERSIZE], msg[HEADERSIZE:]


class NetworkManager:
    """
    This manages all the connections and sessions, including message pickling and
    passing, tracking user sessions, etc.
    """
    def __init__(self, logging=False):
        self.logging = logging
        self._sessions: Dict[sid_t, UserSession] = {}
        self.messages: Dict[sid_t, SimpleNamespace] = {}
        self.namegen = remote.namegen.NameGenerator()
        self.new_game_queue = []
        self.games = []

    def handle_message_to_client(self, client, recv: bytes = b''):
        stored = client.stored
        stored.msg += recv
        if stored.length is None:
            if len(stored.msg) >= HEADERSIZE:
                try:
                    stored.length = int(stored.msg[:HEADERSIZE])
                    stored.msg = stored.msg[HEADERSIZE:]
                except ValueError as e:
                    print("invalid header:", stored.msg[:HEADERSIZE])
                    stored.length = None
                    stored.msg = b''

        if stored.length is not None:
            # We've already read the header...
            if len(stored.msg) >= stored.length:
                # ...and we have the full message
                full_message = pickle.loads(stored.msg[:stored.length])
                client.handle(full_message)
                remaining = stored.msg[stored.length:]
                stored.length = None
                stored.msg = b''

                if remaining:
                    # If there is any received message remaining, it must be the start
                    # of a new message, so recursively call this method
                    self.handle_message_to_client(client, remaining)

    def handle_message_to_session(self, sid: sid_t, recv: bytes = b''):
        """
        Given a possibly incomplete incoming message to a `UserSession` with
        session id `sid`, unpack it and reconstruct it over multiple passes if
        necessary.

        :param sid: the session id of the target session
        :param recv: the pickled message to be unpacked; this may be a
            partial message, in which case the intermediary results are stored
            for later continuation.
        """
        session: UserSession = self._sessions[sid]

        if sid not in self.messages:
            self.messages[sid] = SimpleNamespace(length=None, msg=b'')

        # Two cases. Either:
        # (a) this message doesn't have a constructed header, in which case length is None, or
        # (b) this message has a fully constructed header, in which case length >= 0.

        stored = self.messages[sid]
        stored.msg += recv

        if stored.length is None:
            if len(stored.msg) >= HEADERSIZE:
                try:
                    stored.length = int(stored.msg[:HEADERSIZE])
                    stored.msg = stored.msg[HEADERSIZE:]
                except ValueError as e:
                    print("invalid header:", stored.msg[:HEADERSIZE])
                    del self._sessions[sid]

        if stored.length is not None:
            # We've already read the header...
            if len(stored.msg) >= stored.length:
                # ...and we have the full message
                full_message = pickle.loads(stored.msg[:stored.length])
                session.handle(full_message)
                remaining = stored.msg[stored.length:]
                del self.messages[sid]

                if remaining:
                    # If there is any received message remaining, it must be the start
                    # of a new message, so recursively call this method
                    self.handle_message_to_session(sid, remaining)

    def new_session(self, conn, addr):
        session = UserSession(conn, addr, self)
        self._sessions[session.sid] = session
        print("Creating new UserSession with sid", session.sid, "and username", session.username)
        return session.sid

    def close_session(self, sid: sid_t):
        print("Closing session: sid", sid)
        self._sessions[sid].close()
        del self._sessions[sid]
        if sid in self.new_game_queue:
            self.new_game_queue.remove(sid)

    def get_session(self, sid):
        return self._sessions.get(sid)

    def add_to_new_game_queue(self, sid: sid_t):
        if sid in self.new_game_queue:
            return {"status": "failure", "reason": "already-in-queue"}
        elif sid not in self._sessions:
            return {"status": "failure", "reason": "unknown-sid"}
        else:
            self.new_game_queue.append(sid)

        if len(self.new_game_queue) > 1:
            self.start_new_games()

    def start_new_games(self) -> List[Model]:
        """
        Start as many games as possible from the waiting queue
        :return:
        """
        game = self.start_new_game()
        games = []
        while game:
            games.append(game)
            game = self.start_new_game()
        self.games += games
        return games

    def start_new_game(self) -> Optional[Model]:
        """
        Check if a new game can be started, and if so, start it.
        :return: the new Model object if a game was started, otherwise None
        """
        if len(self.new_game_queue) >= 2:
            sid1, sid2 = self.new_game_queue[:2]
            s1 = self._sessions[sid1]
            s2 = self._sessions[sid2]
            self.new_game_queue = self.new_game_queue[2:]

            # Create associated players
            p1, p2 = Player(s1.username), Player(s2.username)
            game = Game([p1, p2])
            model = Model(game)
            model.register_view(ServerView(sid1, self))
            model.register_view(ServerView(sid2, self))
            s1.start_game(model)
            s2.start_game(model)
            print("Started game between {} and {}".format(p1.name, p2.name))
            s1.outb += self.pack({'type': 'new-game-request-reply',
                                  'data': {'status': 'success',
                                           'game-state': ViewGameState.from_game(game, 0),
                                           'player-number': 0}})
            s2.outb += self.pack({'type': 'new-game-request-reply',
                                  'data': {'status': 'success',
                                           'game-state': ViewGameState.from_game(game, 1),
                                           'player-number': 1}})
            return Model(game)
        else:
            return None

    def add_session_to_queue(self, sid: sid_t) -> Dict[str, str]:
        if sid not in self._sessions:
            return {"status": "failure",
                    "reason": "inactive-session"}
        if sid in self.new_game_queue:
            return {"status": "failure",
                    "reason": "sid-already-waiting"}
        self.new_game_queue.append(sid)

        return {"status": "success"}

    def pack(self, msg) -> bytes:
        return pack(msg)

    def unpack(self, msg: bytes):
        return unpack(msg)


class PacketFormatError(RuntimeError):
    """Runtime error when a poorly formatted packet is encountered"""
    def __init__(self, message=''):
        super().__init__(message)
