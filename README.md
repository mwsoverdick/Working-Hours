# Working-Hours
A python script that parses a Google Maps takeout to log the amount of hours you spend near a specific GPS coordinate. A great way to passively log working hours using Google's data.

## Usage
This file is a standalone script so to use it you must edit the source code [WorkingHours.py](./WorkingHours.py)

The key parameters are

- **`location_history_file`** *The path to the `Location History.json` file provided from [Google Takout](https://takeout.google.com/u/0/settings/takeout)*
- **`work_lat`** *The latitude of your work in degrees*
- **`work_lon`** *The longitude of your work in degrees*
- **`work_range`** *The range in meters around the coordinate defined by `work_lat` and `work_lon` to be considered "at work" (this compensates for GPS noise)*
- **`start_date`** *The date to start counting from*
- **`stop_date`** *The date to stop counting from (None to go to the end of the dataset)*
- **`dur_thresh`** *The duration threshold to be considered "at work" (this compensates for drive-by conditions)*

Run this script using Python 3 with all the parameters defined above. 

This has been tested on a takeout of approx. 780,000 waypoints and computation time on a fully loaded MacBook Pro (mid 2014) is about 1 minute for 9 months worth of waypoints.
