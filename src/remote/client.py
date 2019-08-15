import socket
import selectors
from types import SimpleNamespace

from remote.controller import ClientControllerCLI
from remote.network import NetworkManager, pack
from sys import exit

from remote.states import ClientState
from remote.view import ClientViewCLI


class Client:
    def __init__(self, host='127.0.0.1', port=65432, messages=None):
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.messages = []
        self.responses = []
        self.sel = selectors.DefaultSelector()
        self.nm = NetworkManager()
        self.state = ClientState.NEW
        self._up_to_date = True
        self.username = None
        self.data = None
        self.sid = None
        self.session_key = None
        self.stored = SimpleNamespace(length=None, msg=b'')
        self.game_state = None
        self.view = None
        self.controller = None

    def start_connections(self):
        server_addr = self.addr
        print('starting connection to', server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.data = SimpleNamespace(recv_total=0,
                                    send_total=0,
                                    outb=b'')
        self.sel.register(sock, events, data=self.data)
        self.state = ClientState.CONNECTED

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data:
                self.nm.handle_message_to_client(self, recv_data)
                data.recv_total += 1
            if not recv_data or data.send_total >= 5:
                print('closing connection')
                self.sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if not data.outb:
                self.transition_write(data)
            if data.outb:
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]

    def handle(self, msg):
        self.transition_read(msg)

    def transition_read(self, msg):
        """
        Handle an incoming unpacked message from the server and update states accordingly
        :param msg: unpacked message from the server
        :return:
        """

        if not isinstance(msg, dict) or "type" not in msg:
            raise ValueError("msg must be an unpacked message of the form {\"type\": tp, ...}")

        if 'data' not in msg:
            raise ValueError("All messages must have a data field")

        tp = msg['type']
        data = msg['data']
        state = self.state

        if state == ClientState.REQ_SESSION:
            if tp != "session-initialization-reply":
                raise ValueError("expected session-initialization-reply but got " + str(tp))

            status = data['status']
            if status == "failure":
                print("Error requesting new session, exiting")
                exit(1)
            if status == 'success':
                self.sid = data['sid']
                self.session_key = data['key']
                self.state = ClientState.RECV_SESSION

        elif state == ClientState.SENT_GREETING:
            if tp != 'greeting-reply':
                raise ValueError("expected greeting-reply but got " + str(tp))
            status = data['status']
            if status == 'success':
                self.username = data['username']
                print("Started session as", self.username)
                self.username = data['username']
                self.state = ClientState.FRESH

        elif state == ClientState.REQ_GAME:
            if tp != 'new-game-request-reply':
                raise ValueError("expected new-game-request-reply but got " + str(tp))
            status = data['status']
            if status == 'success':
                self.game_state = data['game-state']
                self._up_to_date = True
                self.view = ClientViewCLI(self.game_state)
                self.controller = ClientControllerCLI(self)
                self.state = ClientState.GAME
                self.view.render()

        elif state == ClientState.GAME:
            if tp != 'game-state-update':
                raise ValueError("expected game-state-update but got " + str(tp))
            self.game_state = data['game-state']
            self._up_to_date = True
            self.view.game_state.update(self.game_state)
            self.view.render()

    def transition_write(self, data):
        """
        Handle outgoing messages, writing to data.outb and updating state appropriately
        :param data:
        :return:
        """
        state = self.state

        if self.state == ClientState.CONNECTED:
            data.outb += pack({"type": "session-initialization", "data": {"sid": None}})
            self.state = ClientState.REQ_SESSION

        elif state == ClientState.RECV_SESSION:
            while True:
                name = input("Enter preferred username (nothing for autogen): ").strip()
                if not name:
                    break
                if name.replace(" ", "").replace("-", "").isidentifier():
                    break
                else:
                    print("Username must contain only letters, numbers, spaces, dashes, and underscores")
            if not name:
                name = None

            data.outb += pack({"type": "greeting", "data": {"username": name}})
            self.state = ClientState.SENT_GREETING

        elif state == ClientState.FRESH:
            print("Requesting game from server...")
            data.outb += pack({"type": "new-game-request", "data": None})
            self.state = ClientState.REQ_GAME

        elif state == ClientState.GAME:
            gs = self.game_state
            if gs.current_player == gs.owner and self._up_to_date:
                cmd = input('\033[1mEnter\033[0m <action> [args...]\n\033[{};1m({}) >>>\033[0m '.format(
                    self.view.formatter.player_colors[gs.current_player],
                    gs.players[gs.current_player].name))
                msg = self.controller.process(cmd)
                if msg['type'] == 'error':
                    print("error:", msg)
                elif msg['type'] == 'empty':
                    self.view.render()
                else:
                    data.outb += self.nm.pack(msg)
                    self._up_to_date = False

    def send_to_model(self, d):
        self.data.outb += self.nm.pack(d)

    def run(self):
        print("running client")
        self.start_connections()
        try:
            while True:
                events = self.sel.select(timeout=1)
                if events:
                    for key, mask in events:
                        self.service_connection(key, mask)
                if not self.sel.get_map():
                    break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

