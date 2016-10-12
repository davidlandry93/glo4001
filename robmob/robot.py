import collections
import json
import _thread
import urllib.parse
import websocket
import time
from robmob.commands import CommandPublisher, LinearMovementCommand, ResetCommand, RotationCommand, MovementCommand



class Robot:

    def __init__(self, robot_ip, port=9090):
        self.ws = None
        self.publisher = None
        self.sensors = {}
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


    def add_sensor(self, sensor):
        self.ws.send(json.dumps(sensor.subscription_message))

        if sensor.TOPIC in self.sensors:
            self.sensors[sensor.TOPIC].append(sensor)
        else:
            self.sensors[sensor.TOPIC] = [sensor]


    def send_command(self, command):
        if self.publisher:
            self.publisher.stop_publishing()
        self.publisher = CommandPublisher()
        self.publisher.start_publishing(self.ws.send, command)


    def disconnect(self):
        self.ws.keep_running = False
        
    def general_movement_command(self, linear, angular, duration):
        self.send_command(MovementCommand(linear, angular))
        time.sleep(duration)
        self.send_command(ResetCommand())
        
    def move(self, speed, duration):
        command = LinearMovementCommand(speed)
        
        self.send_command(command)
        time.sleep(duration)
        self.send_command(ResetCommand())
        
    def rotate(self, speed, duration):
        command = RotationCommand(speed)
        
        self.send_command(command)
        start = time.time()
        time.sleep(duration)
        print(time.time() - start)
        self.send_command(ResetCommand())

    def _on_message(self, _, raw_message):
        parsed_message = json.loads(raw_message)
        message_topic = parsed_message['topic']

        if message_topic in self.sensors:
            [s.on_message(parsed_message) for s in self.sensors[message_topic]]


    def _on_open(self, *args, **kargs):
        pass


    def _on_error(self, *args, **kargs):
        pass


    def _on_close(self, *args, **kargs):
        pass
