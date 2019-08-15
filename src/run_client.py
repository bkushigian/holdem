from remote.client import Client
from sys import argv

port = 65432
if len(argv) > 1:
    port = int(argv[1])

if len(argv) > 2:
    host = argv[2]

client = Client(port=port)
client.run()
