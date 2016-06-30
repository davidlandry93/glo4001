#!/usr/bin/env python3

import collections
import json
import _thread
import urllib.parse
import websocket

from enum import Enum


class Sensors(Enum):
    hokuyo = 1


class HokuyoSensor:
    TOPIC = '/scan'

    def __init__(self, buffer_size=500):
        self.buffer_size = buffer_size
        self.buffer = collections.deque([], maxlen=buffer_size)

        self.subscription_message = json.dumps({'op': 'subscribe',
                                                'type': 'sensor_msgs/LaserScan',
                                                'topic': '/scan'})

        
    def on_message(self, message):
        self.buffer.append(message)

        
    def read_all_data(self):
        old_buffer = self.buffer
        self.buffer = collections.deque([], maxlen=self.buffer_size)

        return old_buffer

    
    def read_data(self):
        try:
            return self.buffer.popleft()
        except IndexError:
            raise IndexError('Le buffeur du capteur est vide')
        
        
    def peek_most_recent_data(self):
        try:
            return self.buffer[len(self.buffer) - 1]
        except IndexError:
            raise IndexError('Le buffeur du capteur est vide')
            

def on_error(ws, error):
    print(error)


def on_close(ws):
    pass
    

def on_open(ws):
    pass
    #_thread.start_new_thread(lambda: ws.send(subscription_message), ())


class Robot:
    SENSORS = {Sensors.hokuyo: HokuyoSensor}

    def __init__(self, robot_ip, port=9090):
        self.ws = None
        self.listened_sensors = {}
        self.robot_url = 'ws://' + robot_ip + ':' + str(port)

        try:
            urllib.parse.urlparse(self.robot_url)
        except ValueError:
            print("L'ip fournie est invalide") 
            print(self.robot_url)


    def connect(self):
        self.ws = websocket.WebSocketApp(self.robot_url,
                                         on_message = self.on_message,
                                         on_error = on_error,
                                         on_close = on_close)
        self.ws.on_open = on_open
        _thread.start_new_thread(self.ws.run_forever, ())

    def listen_to(self, sensor):
        new_sensor = None
        try:
            new_sensor = self.SENSORS[sensor]()
        except KeyError:
            raise ValueError('Capteur non-reconnu')

        self.ws.send(new_sensor.subscription_message)
        self.listened_sensors[new_sensor.TOPIC] = new_sensor

    def disconnect(self):
        self.ws.keep_running = False

    def on_message(self, _, message):
        parsed_message = json.loads(message)
        self.listened_sensors[parsed_message['topic']].on_message(parsed_message)

    def read_sensor_data(self, sensor):
        return self.listened_sensors[self.SENSORS[sensor].TOPIC].read_data()
    
    
    def peek_most_recent_data(self, sensor):
        return self.listened_sensors[self.SENSORS[sensor].TOPIC].peek_most_recent_data()
