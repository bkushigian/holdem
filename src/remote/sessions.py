
class SessionManager:
    _id = -1

    @staticmethod
    def new_sid():
        SessionManager._id += 1
        return SessionManager._id