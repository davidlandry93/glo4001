
from io import BytesIO
import numpy as np
import base64
import collections
from PIL import Image



class Sensor:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.buffer = collections.deque([], maxlen=buffer_size)
        self.subscription_message = {'op': 'subscribe',
                                     'type': self.MESSAGE_TYPE,
                                     'topic': self.TOPIC }


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


    def read_buffer(self):
        old_buffer = self.buffer
        self.buffer = collections.deque([], maxlen=self.buffer_size)
        return self.format_buffer_numpy(old_buffer)
    
    
    def format_buffer_numpy(self, buf):
        return np.asarray(buf)
        


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

    def __init__(self, analog_input_id, buffer_size=100):
        """
        There are two Sharp sensors on the robot. The analog_input_id 0 is the long range sensor 
        and the analog_input_id 1 is the short range sensor.
        """
        super().__init__(buffer_size)
        self.analog_input_id = analog_input_id

        
    def parse_message(self, message):
        return float(message['msg']['analog_input'][self.analog_input_id]) / 4096 * 3.3
    


class KinectRGBSensor(Sensor):
    TOPIC        = '/camera/rgb/image_color/compressed'
    MESSAGE_TYPE = 'sensor_msgs/CompressedImage'
    SAMPLE_RATE  = 30

    def __init__(self, buffer_size=30):
        super().__init__(buffer_size)

        
    def parse_message(self, message):
        image_data = message['msg']['data']
        decompressed_image = Image.open(BytesIO(base64.b64decode(image_data)))

        return decompressed_image

