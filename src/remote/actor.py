from typing import Dict, Any


class Actor:

    def handle(self, msg: Dict[str, Any]):
        raise NotImplementedError()