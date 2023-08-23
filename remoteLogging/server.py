#!/usr/bin/env python3

from websocket_server import WebsocketServer
import threading
import argparse
import sys


parser = argparse.ArgumentParser(description='Accepts input via STDIN and makes it available over a Websocket.')
parser.add_argument("port", nargs='?', default=9001, type=int)

args = parser.parse_args()

logContents = ""
server = WebsocketServer(host = '0.0.0.0', port = args.port)



# Called for every client connecting (after handshake)
def client_joined(client, server):
        print(f"New client connected and was given id {client['id']}")
        server.send_message(client, logContents)



# Called for every client disconnecting
def client_left(client, server):
        print(f"Client({client['id']}) disconnected")



def readFromStdInForever():
        global logContents

        try:
                for line in iter(sys.stdin.readline, b''):
                        if len(line) == 0: continue
                        if line[-1] != '\n': line += '\n'
                        logContents += line
                        server.send_message_to_all(line)
        except KeyboardInterrupt:
                sys.stdout.flush()
                pass



server.set_fn_new_client(client_joined)
server.set_fn_client_left(client_left)

x = threading.Thread(target=readFromStdInForever, args=(), daemon=True)
x.start()
server.run_forever()