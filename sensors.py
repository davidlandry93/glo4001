import numpy as np
import json
import collections


class Sensor:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.buffer = collections.deque([], maxlen=buffer_size)
        self.subscription_message = json.dumps({'op': 'subscribe',
                                                'type': self.MESSAGE_TYPE,
                                                'topic': self.TOPIC
                                                })


    def parse_message(self, message):
        raise NotImplementedError()


    def on_message(self, message):
        self.buffer.append(self.parse_message(message))


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


    def read_all_data(self):
        old_buffer = self.buffer
        self.buffer = collections.deque([], maxlen=self.buffer_size)
        return old_buffer



class HokuyoSensor(Sensor):
    TOPIC        = '/scan'
    MESSAGE_TYPE = 'sensor_msgs/LaserScan'
    SAMPLE_RATE  = 10


    def __init__(self, buffer_size=500):
        super().__init__(buffer_size)


    def parse_message(self, message):
        return {'angle_min': message['msg']['angle_min'],
                'angle_max': message['msg']['angle_max'],
                'range_min': message['msg']['range_min'],
                'range_max': message['msg']['range_max'],
                'ranges'   : np.array(message['msg']['ranges']).astype(np.float32)
                }
