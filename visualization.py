import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation


class Visualizer:
    
    def __init__(self, robot):
        self.robot = robot
        #self.animation_step_millisec = math.floor(1000 / self.sensor.sample_rate)
        
    
    def plot_data(self):
        fig, ax = plt.subplots(1,1, subplot_kw=dict(projection='polar'))

        ax.grid(True)
        ax.set_rmax(3.0)
        ax.set_rmin(0.0)
        ax.set_theta_zero_location('N')
        
        last_data = self.robot.read_sensor_data(Sensors.hokuyo)['msg']
        ranges = np.array(last_data['ranges'])
        angles = np.arange(last_data['angle_min'], last_data['angle_max'] + last_data['angle_increment'], 
                           last_data['angle_increment'])
        
        ranges = ranges.astype('float32')
        
        
        scatter_plot = ax.scatter(angles, ranges, color='b', s=2, animated=True)
        
        plt.show()
        
        
    def animate_sensor(self, animation_length_second=2):
        fig, ax = plt.subplots(1,1, subplot_kw=dict(projection='polar'))

        ax.grid(True)
        ax.set_rmax(3.0)
        ax.set_rmin(0.0)
        ax.set_theta_zero_location('N')
        
        last_data = self.robot.read_sensor_data(Sensors.hokuyo)['msg']
        ranges = np.array(last_data['ranges'])
        angles = np.arange(last_data['angle_min'], last_data['angle_max'] + last_data['angle_increment'], 
                           last_data['angle_increment'])
        
        ranges = ranges.astype('float32')
        
        scatter_plot = ax.scatter(angles, ranges, color='b', s=2, animated=True)
        
        def init_frame():
            scatter_plot.set_array([])
            return (scatter_plot,)
        
        def animate(i):
            last_data = self.robot.peek_most_recent_data(Sensors.hokuyo)['msg']
            ranges = np.array(last_data['ranges'])
            ranges = np.nan_to_num(ranges.astype('float32'))
            angles = np.arange(last_data['angle_min'], last_data['angle_max'] + last_data['angle_increment'], 
                               last_data['angle_increment'])
            
            table = np.zeros((ranges.shape[0], 2))
            table[:, 0] = angles
            table[:, 1] = ranges
            scatter_plot.set_offsets(table)
            
            return scatter_plot,
        
        return animation.FuncAnimation(fig, animate, frames=100, interval=100, blit=True)
