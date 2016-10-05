
from io import BytesIO
import math
import numpy as np
import base64
import collections
import time
from PIL import Image



class Sensor:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.buffer = collections.deque([], maxlen=buffer_size)
        self.continuous_buffer = None
        self.subscription_message = {'op': 'subscribe',
                                     'type': self.MESSAGE_TYPE,
                                     'topic': self.TOPIC }
        self.unsubscribe_message = {'op': 'ubsubscribe',
                                    'topic': self.TOPIC}


    def on_message(self, message):
        parsed_message = self.parse_message(message)
        self.buffer.append(parsed_message)
        if self.continuous_buffer != None:
            self.continuous_buffer.append(parsed_message)


    def read_data(self):
        try:
            return self.buffer.popleft()
        except IndexError:
            raise IndexError('Le buffeur du capteur est vide')


    def peek_data(self):
        try:
            return self.buffer[-1]
        except IndexError:
            raise IndexError('Le buffeur du capteur est vide')


    def read_buffer(self):
        old_buffer = self.buffer
        self.buffer = collections.deque([], maxlen=self.buffer_size)
        return self.format_buffer_numpy(old_buffer)
    
    
    def peek_buffer(self):
        return self.format_buffer_numpy(self.buffer)
    
    
    def sample_data_for_x_sec(self, x):
        self.continuous_buffer = []
        time.sleep(x)
        samples, self.continuous_buffer = self.continuous_buffer, None
        return self.format_buffer_numpy(samples)
        
    
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
    TOPIC        = '/mobile_base/sensors/core'
    MESSAGE_TYPE = 'kobuki_msgs/SensorState'
    SAMPLE_RATE  = 50
    
    #Calibration table of the high range sharp sensor, for 15+ cm.
    HIGH_RANGE_CALIB_TABLE =  np.asarray([[15, 2.76], [20, 2.53], [30, 1.99], [40, 1.53], [50, 1.23], [60, 1.04], [70, 0.91], [80, 0.82], [90, 0.72], [100, 0.66], [110, 0.6], [120, 0.55], [130, 0.50], [140, 0.46], [150, 0.435], [150, 0]])

    def __init__(self, analog_input_id, buffer_size=100):
        """
        There are two Sharp sensors on the robot. The analog_input_id 0 is the long range sensor 
        and the analog_input_id 1 is the short range sensor.
        """
        super().__init__(buffer_size)
        self.analog_input_id = analog_input_id

        
    def parse_message(self, message):
        return float(message['msg']['analog_input'][self.analog_input_id]) / 4096 * 3.3
    
    
    
class GyroSensor(Sensor):
    TOPIC        = '/mobile_base/sensors/imu_data_raw'
    MESSAGE_TYPE = 'sensor_msgs/Imu'
    SAMPLE_RATE  = 108
    
    
    def __init__(self, buffer_size=200):
        super().__init__(buffer_size)
        
        
    def parse_message(self, message):
        return {
            'x': math.degrees(message['msg']['angular_velocity']['x']),
            'y': math.degrees(message['msg']['angular_velocity']['y']),
            'z': math.degrees(message['msg']['angular_velocity']['z'])
        }
    
    
    def format_buffer_numpy(self, buf):
        return np.asarray(list(map((lambda m: [m['x'], m['y'], m['z']]), buf)))
    

    
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

