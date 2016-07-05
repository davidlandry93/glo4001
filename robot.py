import collections
import json
import _thread
import urllib.parse
import websocket
from sensors import Sensor

class Robot:

    def __init__(self, robot_ip, port=9090):
        self.ws = None
        self.listened_sensors = {}
        self.robot_url = 'ws://' + robot_ip + ':' + str(port)

        try:
            urllib.parse.urlparse(self.robot_url)
        except ValueError:
            print("L'adresse IP fournie est invalide") 
            print(self.robot_url)


    def connect(self):
        self.ws = websocket.WebSocketApp(self.robot_url,
                                         on_message = self._on_message,
                                         on_error = self._on_error,
                                         on_close = self._on_close)
        self.ws.on_open = self._on_open
        _thread.start_new_thread(self.ws.run_forever, ())


    def listen_to(self, sensor):
        self.ws.send(sensor.subscription_message)
        self.listened_sensors[sensor.TOPIC] = sensor


    def disconnect(self):
        self.ws.keep_running = False


    def _on_message(self, _, message):
        message_dictionary = json.loads(message)
        message_topic = message_dictionary['topic']
        self.listened_sensors[message_topic].on_message(message_dictionary)


    def _on_open(self, *args, **kargs):
        pass


    def _on_error(self, *args, **kargs):
        pass


    def _on_close(self, *args, **kargs):
        pass
