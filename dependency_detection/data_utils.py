#!/usr/bin/python

import numpy as np
import pandas as pd
import yaml

class DataUtils(object):
    def __init__(self):
        pass

    @staticmethod
    def load_data_csv(filename, keys, number_of_wheels):
        csv_data = pd.read_csv(filename)
        data = None
        variables = []
        for wheel in range(number_of_wheels):
            wheel_data = None
            for k in keys:
                if k != '%time':
                    # get the key for current wheel index
                    current_key = k.replace('0', str(wheel))
                else:
                    current_key = k

                if wheel_data is None:
                    wheel_data = np.array(csv_data[current_key].values)[:, np.newaxis]
                else:
                    wheel_data = np.hstack((wheel_data, np.array(csv_data[current_key].values)[:, np.newaxis]))
                if (wheel == 0):
                    if current_key != '%time':
                        variable_name = current_key.split('.')[-1]
                    else:
                        variable_name = 'timestamp'
                    variables.append(variable_name)
            if (data is None):
                data = wheel_data[np.newaxis, :, :]
            else:
                data = np.vstack((data, wheel_data[np.newaxis, :, :]))
        data[:, :, 0] = data[:, :, 0] // 10**8
        #data.shape = (number_of_wheels x data_samples x number_of_variables)
        return data, variables

    @staticmethod
    def load_data_rosbag(filename, topic, command_attr, sensor_attr, number_of_wheels):
        import rosbag
        bag = rosbag.Bag(filename)
        data = None
        variables = ['timestamp']
        variables.extend(command_attr)
        variables.extend(sensor_attr)
        for topic, msg, t in bag.read_messages(topics=[topic]):
            data_sample = []
            for i in range(number_of_wheels):
                row = []
                row.append(t.to_time())
                for c in command_attr:
                    row.append(getattr(msg.commands[i], c))
                for s in sensor_attr:
                    row.append(getattr(msg.sensors[i], s))
                data_sample.append(row)

            data_sample = np.array(data_sample)
            if (data is None):
                data = data_sample[np.newaxis, :, :]
            else:
                data = np.vstack((data, data_sample[np.newaxis, :, :]))
        data = np.swapaxes(data, 0, 1)
        #data.shape = (number_of_wheels x data_samples x number_of_variables)
        return data, variables

    @staticmethod
    def load_events_rosbag(filename, topic):
        import rosbag
        bag = rosbag.Bag(filename)
        event_times = []
        for topic, msg, t in bag.read_messages(topics=[topic]):
            event_times.append(t.to_time())
        return event_times

    @staticmethod
    def get_window(data, start_row_index, window_size):
        if start_row_index + window_size > data.shape[0]:
            return None
        return data[start_row_index:start_row_index+window_size]
