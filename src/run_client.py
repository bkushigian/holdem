from remote.client import Client
from sys import argv

port = 65432
host = '127.0.0.1'
if len(argv) > 1:
    port = int(argv[1])

if len(argv) > 2:
    host = argv[2]

print("host", host, "port", port)
client = Client(host=host, port=port)
client.run()
