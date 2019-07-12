# Dependency_Detection


## Usage
```
usage: main.py [-h] [--data_collection DATA_COLLECTION]
               [--event_collection EVENT_COLLECTION]
               [--significance_level [SIGNIFICANCE_LEVEL]]
               [--plot_type [{heatmap,timeseries,simple_plot}]]
               [--window_size [WINDOW_SIZE]] [--wheel1 [{0,1,2,3}]]
               [--var1 [VAR1]] [--wheel2 [{0,1,2,3}]] [--var2 [VAR2]]
               {rosbag,csv,blackbox} ds

Dependency detection using Granger Causality tests

positional arguments:
  {rosbag,csv,blackbox}
                        Data source type
  ds                    Data source (file location, database name etc.)

optional arguments:
  -h, --help            show this help message and exit
  --data_collection DATA_COLLECTION
                        collection containing smart wheel data
  --event_collection EVENT_COLLECTION
                        collection containing event annotations
  --significance_level [SIGNIFICANCE_LEVEL]
  --plot_type [{heatmap,timeseries,simple_plot}]
  --window_size [WINDOW_SIZE]
                        window size used for timeseries plots
  --wheel1 [{0,1,2,3}]  Wheel index for variable 1 used for timeseries and
                        heatmap plots
  --var1 [VAR1]         Variable 1 used for timeseries plots
  --wheel2 [{0,1,2,3}]  Wheel index for variable 2 used for timeseries and
                        heatmap plots
  --var2 [VAR2]         Variable 2 used for timeseries plots
```

### examples:
```
python main.py csv data/cable_faults/power_unplugged_trial_2.csv --plot_type heatmap
python main.py csv data/cable_faults/straight_pow_merge.csv --plot_type timeseries --var1 current_1_w --var2 current_2_w

```
