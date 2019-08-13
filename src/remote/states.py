from enum import Enum, auto


class ClientState(Enum):
    """
    States that the client can be in

    Attributes
    """
    ERROR = auto()
    NEW = auto()
    CONNECTED = auto()
    REQ_SESSION = auto()
    RECV_SESSION = auto()
    SENT_GREETING = auto()
    FRESH = auto()
    REQ_GAME = auto()
    GAME = auto()
    GAME_OVER = auto()


class UserSessionState(Enum):
    ERROR = auto()
    NEW = auto()
    SENT_SESSION_DATA = auto()
    FRESH = auto()
    GAME_QUEUE = auto()
    GAME = auto()

