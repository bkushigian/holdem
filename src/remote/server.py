import socket
import selectors
import time

from remote.network import NetworkManager, pack
from typing import List
from remote.util import sid_t

import logging

LOGGER = logging.getLogger(__name__)


class Server:

    def __init__(self, host='127.0.0.1', port=65432):
        print("Spinning up server")
        self.sel = selectors.DefaultSelector()
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.nm = NetworkManager()
        self.waiting: List[sid_t] = []    # Clients waiting to join a game

    def accept_wrapper(self, sock):
        print("Server.accept_wrapper")
        conn, addr = sock.accept()
        conn.setblocking(False)
        sid = self.nm.new_session(conn, addr)
        self.waiting.append(sid)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=sid)

    def service_connection(self, key, mask):
        sock = key.fileobj
        sid = key.data
        session = self.nm.get_session(sid)
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data:
                self.nm.handle_message_to_actor(actor=session, recv=recv_data)
            else:
                print('closing connection to', session.addr)
                self.nm.close_session(sid)
                self.sel.unregister(sock)
        if mask & selectors.EVENT_WRITE:
            if session.outb:
                sent = sock.send(session.outb)
                session.outb = session.outb[sent:]

    def run(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(self.addr)
        s.listen()
        print('listening on', self.addr)
        s.setblocking(False)
        self.sel.register(s, selectors.EVENT_READ, data=None)
        # conn, addr = s.accept()
        while True:
            try:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask)
                self.nm.start_new_games()
                time.sleep(0.0001)    # Share the love (i.e., the cpu)
            except KeyboardInterrupt:
                print("caught keyboard interrupt, exiting")
            finally:
                s.close()
