class UserSession:
    _id = -1

    def __init__(self, conn, addr, user_name=None):
        print("Creating user session")
        self.conn = conn
        self.addr = addr
        self.user_name = user_name

        self.sid = UserSession._new_id()
        self.game = None
        self.on_exit = []           # A list of callables to call on exit

        self.outb = b''       # outgoing message
        self.recv = []        # Recieved messages

    def close(self):
        for f in self.on_exit:
            f()
        if self.conn:
            self.conn.close()

    def handle(self, msg: bytes):
        self.recv.append(msg)
        problem = msg['problem']
        print(problem)
        result = eval(problem)
        print('problem', problem, 'result', result)
        self.outb = bytes(str(eval(problem)), 'utf-8')

    @staticmethod
    def _new_id():
        UserSession._id += 1
        return UserSession._id


