from typing import Dict, Any


class Actor:
    _id = -1

    def __init__(self):
        self.sid = Actor._new_id()
        self.outb = b''     # outgoing message

    def handle(self, msg: Dict[str, Any]):
        raise NotImplementedError()

    def _new_id():
        Actor._id += 1
        return Actor._id

