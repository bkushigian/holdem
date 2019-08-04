import pickle
from remote.usersession import UserSession
import remote.namegen
from typing import Dict
from types import SimpleNamespace


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
        session = UserSession(conn, addr)
        self._sessions[session.sid] = session
        self.namegen.generate_session_username(session)
        print("Creating new UserSession with sid", session.sid, "and username", session.user_name)
        return session.sid

    def close_session(self, sid: sid_t):
        print("Closing session: sid", sid)
        self._sessions[sid].close()

    def get_session(self, sid):
        return self._sessions[sid]


class PacketFormatError(RuntimeError):
    """Runtime error when a poorly formatted packet is encountered"""
    def __init__(self, message=''):
        super().__init__(message)
