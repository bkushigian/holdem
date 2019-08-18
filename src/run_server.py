from remote.server import Server
from sys import argv

host = '127.0.0.1'
port = 65432
if len(argv) > 1:
    port = int(argv[1])

if len(argv) > 2:
    host = argv[2]
    if host == 'all':
        host = ''

server = Server(host=host, port=port)
server.run()
