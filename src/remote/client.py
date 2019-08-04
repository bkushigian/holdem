import socket
import time
import selectors
import types
from remote.network import NetworkManager, pack, unpack
import random


class Client:
    def __init__(self, host='127.0.0.1', port=65432, messages=None):
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.messages = []
        self.responses = []
        self.sel = selectors.DefaultSelector()
        self.nm = NetworkManager()

    def start_connections(self):
        server_addr = self.addr
        print('starting connection to', server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(recv_total=0,
                                     send_total=0,
                                     outb=b'')
        self.sel.register(sock, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data:
                print('recv_data', recv_data)
                data.recv_total += 1
            if not recv_data or data.send_total >= 5:
                print('closing connection')
                self.sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if not data.outb and data.send_total < 5:
                lhs = random.randint(0, 100)
                rhs = random.randint(0, 100)
                op = random.choice(('+', '-', '*'))
                problem = {"id": len(self.messages), "problem": "{} {} {}".format(lhs, op, rhs)}
                print("Created problem:", problem)
                self.messages.append((problem, eval(problem['problem'])))
                data.outb += pack(problem)
                data.send_total += 1
            if data.outb:
                print('sending', repr(data.outb), 'to connection')
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]
                time.sleep(0.5)

    def run(self):
        print("running client")
        self.start_connections()
        try:
            while True:
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
