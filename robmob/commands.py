import time
import _thread
import json


DO_NOT_SEND_REPEATEDLY_FLAG = None
LINEAR_SPEED = 0.12
ANGULAR_SPEED = 0.6 

class RosTwistMessage:
    
    def __init__(self, linear_velocity, angular_velocity):
        self.message = {
            'linear': {
                'x': linear_velocity,
                'y': 0.0,
                'z': 0.0
            },
            'angular': {
                'x': 0.0,
                'y': 0.0,
                'z': angular_velocity
            }
        }
    
    
    
class CommandPublisher:
    
    def __init__(self):
        self.stop = False
        
        
    def start_publishing(self, send_fn, command):
        command_json = json.dumps(command.message_to_publish)
        frequency_hz = command.publish_frequency_hz
        
        if frequency_hz == DO_NOT_SEND_REPEATEDLY_FLAG:
            send_fn(command_json)
        else:
            _thread.start_new_thread(self._publish_repeatedly, (send_fn, command_json, frequency_hz))
            
        
    def stop_publishing(self):
        self.stop = True
    
    
    def _publish_repeatedly(self, send_fn, json, frequency_hz):
        sleep_time_sec = 1.0 / frequency_hz
        while not self.stop:
            send_fn(json)
            time.sleep(sleep_time_sec)
            
            
            
class Command:
    def __init__(self, send_frequency_hz=10):
        self.publish_frequency_hz = send_frequency_hz
        self.message_to_publish = {
            'op': 'publish',
            'topic': '/mobile_base/commands/velocity'
            }
        
        
    def _add_twist_message(self, twist):
        self.message_to_publish['msg'] = twist.message
        
        
        
class ResetCommand(Command):
    def __init__(self):
        super().__init__(DO_NOT_SEND_REPEATEDLY_FLAG)
        self._add_twist_message(RosTwistMessage(0, 0))

        
        
class TurnLeftCommand(Command):
    def __init__(self):
        super().__init__()
        self._add_twist_message(RosTwistMessage(0, ANGULAR_SPEED))
        
        
        
class TurnRightCommand(Command):
    def __init__(self):
        super().__init__()
        self._add_twist_message(RosTwistMessage(0, -ANGULAR_SPEED))
        
        
        
class MoveForwardCommand(Command):
    def __init__(self, boost=False):
        super().__init__()
        self._add_twist_message(RosTwistMessage(3 * LINEAR_SPEED if boost else LINEAR_SPEED, 0))
        
        
        
class MoveBackwardCommand(Command):
    def __init__(self):
        super().__init__()
        self._add_twist_message(RosTwistMessage(-LINEAR_SPEED, 0))
        
        