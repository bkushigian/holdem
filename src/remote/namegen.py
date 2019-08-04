from os import path as osp
import random
from remote.usersession import UserSession


class NameGenerator:
    counter = 0

    def __init__(self):
        self.usernames = set()
        self.token_name_map = {}

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

    def generate_session_username(self, session:UserSession):
        name = self.generate_username()
        token = NameGenerator.new_token()
        self.token_name_map[token] = name

        def release():
            del self.token_name_map[token]
            self.remove_username(name)

        session.user_name = name
        session.on_exit.append(release)
        return name

    def remove_username(self, name):
        self.usernames.remove(name)

    @staticmethod
    def new_token():
        NameGenerator.counter += 1
        return NameGenerator.counter - 1

