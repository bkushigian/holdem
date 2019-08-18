from typing import Dict, Any

from remote.sessions import SessionManager


class Actor:

    def __init__(self):
        self.sid = SessionManager.new_sid()
        self.outb = b''     # outgoing message

    def handle(self, msg: Dict[str, Any]):
        raise NotImplementedError()