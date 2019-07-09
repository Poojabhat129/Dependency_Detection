#!/usr/bin/python

import numpy as np
import yaml
import datetime
import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from dependency_detection.data_utils import DataUtils
from dependency_detection.granger_causality import GrangerCausality


def plot_data(data, all_variables, wheel_index_1, var1, wheel_index_2, var2, variable_units, event_times=None):
    wheel_index = 0
    x1 = data[wheel_index][:, all_variables.index(var1)]
    x2 = data[wheel_index][:, all_variables.index(var2)]
    t = data[wheel_index][:, all_variables.index('timestamp')]
    t = [datetime.datetime.fromtimestamp(val) for val in t]

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    var1_plot, = ax1.plot(t, x1, color='m')
    ax1.set_title(var1)
    ax1.set_ylabel(var1 + '(' + variable_units[var1] + ')')
    var2_plot, = ax2.plot(t, x2, color='b')
    ax2.set_title(var2)
    ax2.set_ylabel(var2 + '(' + variable_units[var2] + ')')
    # set current axis
    plt.sca(ax1)
    plt.legend([var1_plot, var2_plot], [var1, var2])
    if (event_times is not None):
        for e in event_times:
            ax1.axvline(x=datetime.datetime.fromtimestamp(e), color='#3b7fed', linestyle=':')
            ax2.axvline(x=datetime.datetime.fromtimestamp(e), color='#3b7fed', linestyle=':')
    fig.tight_layout()
    plt.show()

def plot_windowed_granger(data, all_variables, wheel_index_1, var1, wheel_index_2, var2, window_size, granger_causality, variable_units, event_times=None):
    start_row_index = 0
    p_values = np.zeros((window_size-1,))
    while True:
        window_data_1 = DataUtils.get_window(data[wheel_index_1], start_row_index, window_size)
        window_data_2 = DataUtils.get_window(data[wheel_index_2], start_row_index, window_size)
        if window_data_1 is None or window_data_2 is None:
            break
        x1 = window_data_1[:, all_variables.index(var1)]
        x2 = window_data_2[:, all_variables.index(var2)]
        causal, lag, p_value = granger_causality.is_granger_causal(x1, x2)
        p_values = np.hstack((p_values, p_value))
        start_row_index += 1
    x1 = data[wheel_index_1][:, all_variables.index(var1)]
    x2 = data[wheel_index_2][:, all_variables.index(var2)]
    t = data[wheel_index_1][:, all_variables.index('timestamp')]
    t = [datetime.datetime.fromtimestamp(val) for val in t]

    nans = np.zeros((window_size,))
    nans.fill(np.nan)
    p_values = np.hstack((p_values, nans))
    p_values = p_values[window_size:window_size+x1.shape[0]]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    var1_plot, = ax1.plot(t, x1, color='m')
    ax1.set_title(var1)
    ax1.set_ylabel(var1 + ' (' + variable_units[var1] + ')')
    var2_plot, = ax2.plot(t, x2, color='b')
    ax2.set_title(var2)
    ax2.set_ylabel(var2 + ' (' + variable_units[var2] + ')')
    pval_plot, = ax3.plot(t, p_values, color='g')
    ax3.set_ylim([0.0, 1.0])
    ax3.set_title('p-values')
    ax3.set_ylabel('p-value')
    # set current axis
    plt.sca(ax1)
    plt.legend([var1_plot, var2_plot, pval_plot], [var1, var2, 'p-value'])
    plt.sca(ax3)
    plt.axhline(y=0.05, color='r', linestyle=':')
    if (event_times is not None):
        for e in event_times:
            ax1.axvline(x=datetime.datetime.fromtimestamp(e), color='#3b7fed', linestyle=':')
            ax2.axvline(x=datetime.datetime.fromtimestamp(e), color='#3b7fed', linestyle=':')
            ax3.axvline(x=datetime.datetime.fromtimestamp(e), color='#3b7fed', linestyle=':')
    fig.tight_layout()
    plt.show()

def generate_heatmap(data, all_variables, selected_variables, granger_causality, wheel_index_1, wheel_index_2):
    fig, ax = plt.subplots(figsize=(10,10))
    p_values = np.empty((len(selected_variables), len(selected_variables)))
    imvalues = np.empty((len(selected_variables), len(selected_variables)))
    for idx1, v1 in enumerate(selected_variables):
        for idx2, v2 in enumerate(selected_variables):
            # only use data from wheel 1
            x1 = data[wheel_index_1][:, all_variables.index(v1)]
            x2 = data[wheel_index_2][:, all_variables.index(v2)]
            causal, lag, p_value = granger_causality.is_granger_causal(x1, x2, lag=30)
            p_value = np.around(p_value, decimals=2)
            p_values[idx1, idx2] = p_value
            if (causal):
                imvalues[idx2, idx1] = 0.0
            else:
                imvalues[idx2, idx1] = 0.5
            txt = ax.text(idx1, idx2, p_value, ha="center", va="center")

    im = ax.imshow(imvalues,'Blues')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.3)
    cbar = ax.figure.colorbar(im, cax=cax)
    # We want to show all ticks...
    ax.set_xticks(np.arange(len(selected_variables)))
    ax.set_yticks(np.arange(len(selected_variables)))
    ax.set_xticklabels(selected_variables)
    ax.set_yticklabels(selected_variables)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax.set_title("p-values")
    fig.tight_layout()
    plt.show()
    plt.savefig('data/heatmap.png')


def main():
    parser = argparse.ArgumentParser(description='Dependency detection using Granger Causality tests')
    parser.add_argument('dstype', type=str, choices=['rosbag', 'csv', 'blackbox'], help='Data source type')
    parser.add_argument('ds', type=str, help='Data source (file location, database name etc.)')
    parser.add_argument('--data_collection', default=None, type=str, help='collection containing smart wheel data')
    parser.add_argument('--event_collection', default=None, type=str, help='collection containing event annotations')
    parser.add_argument('--significance_level', nargs='?', default=0.05, type=float)
    parser.add_argument('--plot_type', nargs='?', choices=['heatmap', 'timeseries', 'simple_plot'], default='timeseries')
    parser.add_argument('--window_size', nargs='?', default=45, type=int, help='window size used for timeseries plots')
    parser.add_argument('--wheel1', nargs='?', default=0, type=int, choices=[0, 1, 2, 3], help='Wheel index for variable 1 used for timeseries and heatmap plots')
    parser.add_argument('--var1', nargs='?', default='current_1_w', type=str, help='Variable 1 used for timeseries plots')
    parser.add_argument('--wheel2', nargs='?', default=0, type=int, choices=[0, 1, 2, 3], help='Wheel index for variable 2 used for timeseries and heatmap plots')
    parser.add_argument('--var2', nargs='?', default='current_2_w', type=str, help='Variable 2 used for timeseries plots')


    args = parser.parse_args()

    config = yaml.load(open('config/config.yaml'))
    selected_variables = config['granger_tests']['selected_variables']
    variable_units = config['variable_units']
    granger_causality = GrangerCausality(significance_level=args.significance_level)

    event_times = None

    if (args.dstype == 'rosbag'):
        commands_attr = config['rosbag_config']['commands']
        sensors_attr = config['rosbag_config']['sensors']
        number_of_wheels = config['rosbag_config']['number_of_wheels']
        data_topic = config['rosbag_config']['data_topic']
        event_topic = config['rosbag_config']['event_topic']
        data, all_variables = DataUtils.load_data_rosbag(args.ds, data_topic, commands_attr, sensors_attr, number_of_wheels)
        data = DataUtils.remove_nan_inf(data)
        event_times = DataUtils.load_events_rosbag(args.ds, event_topic)
    elif (args.dstype == 'csv'):
        keys = config['csv_config']['keys']
        number_of_wheels = config['csv_config']['number_of_wheels']
        data, all_variables = DataUtils.load_data_csv(args.ds, keys, number_of_wheels)
    elif (args.dstype == 'blackbox'):
        commands_attr = config['blackbox_config']['commands']
        sensors_attr = config['blackbox_config']['sensors']
        number_of_wheels = config['blackbox_config']['number_of_wheels']
        data_coll = args.data_collection
        event_coll = args.event_collection
        if (data_coll is None):
            data_coll = config['blackbox_config']['default_data_collection']
        if (event_coll is None):
            event_coll = config['blackbox_config']['default_event_collection']
        data, all_variables = DataUtils.load_data_blackbox(args.ds, data_coll, commands_attr, sensors_attr, number_of_wheels)
        data = DataUtils.remove_nan_inf(data)
        event_times = DataUtils.load_events_blackbox(args.ds, event_coll)

    wheel_index_1 = args.wheel1
    wheel_index_2 = args.wheel2
    if (args.plot_type == 'heatmap'):
        generate_heatmap(data, all_variables, selected_variables, granger_causality, wheel_index_1, wheel_index_2)
    elif (args.plot_type == 'timeseries'):
        var1 = args.var1
        var2 = args.var2
        window_size = args.window_size
        plot_windowed_granger(data, all_variables, wheel_index_1, var1, wheel_index_2, var2, window_size, granger_causality, variable_units, event_times)
    elif (args.plot_type == 'simple_plot'):
        var1 = args.var1
        var2 = args.var2
        plot_data(data, all_variables, var1, var2, variable_units, event_times)

if __name__ == "__main__":
    main()
