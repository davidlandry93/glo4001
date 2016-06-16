#!/usr/bin/env python3

import time
import json
import _thread
import websocket

#subscription_message = json.dumps({
#    'op': 'subscribe',
#    'type': 'sensor_msgs/LaserScan',
#    'topic': '/scan'})

def on_message(ws, message):
    message = json.loads(message)
    #print(json.dumps(message))


def on_error(ws, error):
    print(error)


def on_close(ws):
    pass
    

def on_open(ws):
    _thread.start_new_thread(lambda: ws.send(subscription_message), ())


class Robot:
    def __init__(self, robot_url, port=9090):
        self.robot_url = robot_url
        self.port = port
        self.ws = None

    def connect(self):
        self.ws = websocket.WebSocketApp(self.robot_url + ':' + str(self.port),
                                         on_message = on_message,
                                         on_error = on_error,
                                         on_close = on_close)
        self.ws.on_open = on_open
        _thread.start_new_thread(self.ws.run_forever, ())


    def disconnect(self):
        self.ws.keep_running = False
