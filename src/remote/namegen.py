from os import path as osp
import random
from remote.usersession import UserSession


class NameGenerator:
    counter = 0

    def __init__(self):
        self.usernames = set()
        self.sid_map = {}

        with open(osp.join(osp.dirname(__file__), "..", "..", "data", "adjectives")) as f:
            self.adjectives = [l.strip() for l in f.readlines()]
        with open(osp.join(osp.dirname(__file__), "..", "..", "data", "animals")) as f:
            self.nouns = [l.strip() for l in f.readlines()]

    def name_is_available(self, name):
        return name not in self.usernames

    def generate_username(self):
        while True:
            name = "{} {}".format(random.choice(self.adjectives), random.choice(self.nouns))
            if name not in self.usernames:
                self.usernames.add(name)
                return name

    def generate_session_username(self, session: UserSession):
        """
        After ensuring that the session doesn't already have a username, generate a
        fresh username, store it in the session.username field, and store the name
        and the session's sid. Finally, pass a 'release' function to the session to
        release the resources on close.

        :param session:
        :return: The appropriate data portion of a greeting-reply message
        """
        print('generate_session_username(): sid:{}'.format(session.sid))
        sid = session.sid
        if sid in self.sid_map:
            return {'status': 'failure', 'reason': 'session-already-has-username'}

        name = self.generate_username()
        self.sid_map[sid] = name

        def release():
            self.remove_username(name)
            del self.sid_map[sid]

        session.username = name
        session.on_exit.append(release)
        return {'status': 'success', 'username': name}

    def request_session_username(self, session: UserSession, name: str):
        print('request_session_username(): sid:{}, name:{}'.format(session.sid, name))
        sid = session.sid
        if sid in self.sid_map:
            return {'status': 'failure', 'reason': 'session-already-has-username'}
        if name in self.usernames:
            return {'status': 'failure', 'reason': 'name-unavailable'}
        self.sid_map[sid] = name
        self.usernames.add(name)
        session.username = name

        def release():
            self.remove_username(name)
            del self.sid_map[sid]

        session.on_exit.append(release)
        return {'status': 'success', 'username': name}

    def remove_username(self, name):
        self.usernames.remove(name)

