import socket
import time
import selectors
from types import SimpleNamespace
from remote.network import NetworkManager, pack
from sys import exit

from remote.states import ClientState


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
        self.username = None
        self.data = None
        self.sid = None
        self.session_key = None
        self.stored = SimpleNamespace(length=None, msg=b'')

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
                print('sending', repr(data.outb), 'to connection')
                sent = sock.send(data.outb)
                print('sent', sent, 'bytes')
                data.outb = data.outb[sent:]
                time.sleep(0.5)

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
        print("transition_read: state:{} tp:{} data:{}".format(state, tp, data))

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
            status = data['status']
            if status == 'success':
                self.username = data['username']
                print("Started session as", self.username)
                self.username = data['username']
                self.state = ClientState.FRESH

    def transition_write(self, data):
        """
        Handle outgoing messages, writing to data.outb and updating state appropriately
        :param data:
        :return:
        """
        state = self.state
        print("transition_write: state:{}".format(state))

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


    def run(self):
        print("running client")
        self.start_connections()
        try:
            while True:
                time.sleep(0.5)
                events = self.sel.select(timeout=1)
                if events:
                    for key, mask in events:
                        print('mask', mask)
                        self.service_connection(key, mask)
                if not self.sel.get_map():
                    break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

