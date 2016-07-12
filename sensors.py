import numpy as np
import json, base64
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


    def peek_data(self):
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
        return {'angle_min':       message['msg']['angle_min'],
                'angle_max':       message['msg']['angle_max'],
                'angle_increment': message['msg']['angle_increment'],
                'range_min':       message['msg']['range_min'],
                'range_max':       message['msg']['range_max'],
                'ranges'   :       np.nan_to_num(np.array(message['msg']['ranges']).astype(np.float32))
                }



class SharpSensor(Sensor):
    TOPIC   = '/mobile_base/sensors/core'
    MESSAGE_TYPE = 'kobuki_msgs/SensorState'
    SAMPLE_RATE = 50

    def __init__(self, analogInputId, buffer_size=10000):
        super().__init__(buffer_size)
        self.analogInputId = analogInputId

    def parse_message(self, message):
        return {'signal_strength':  message['msg']['analog_input'][self.analogInputId] }



class KinectRGBSensor(Sensor):
    #TOPIC        = '/camera/rgb/image_color/compressed'
    TOPIC = '/camera/rgb/image_color'
    MESSAGE_TYPE = 'sensor_msgs/Image'
    SAMPLE_RATE  = 30

    def __init__(self, buffer_size=50):
        super().__init__(buffer_size)

    def parse_message(self, message):
        npimg = np.frombuffer(base64.decodebytes(bytes(message['msg']['data'], encoding='UTF-8')), dtype=np.uint8)
        npimg.shape
        npimg = npimg.reshape((480*640,3))
        npimg = np.fliplr(npimg)
        npimg = npimg.reshape((480, 640, 3))

        return npimg
