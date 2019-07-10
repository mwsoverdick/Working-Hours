import json
import datetime
import statistics
from geopy.distance import great_circle
from geopy.distance import geodesic

# Path to location history file
location_history_file = "./Takeout/Location History/Location History.json"

# Work coordinates
work_lat = 45.4845391
work_lon = -122.67612

# Meters to consider "near" work
work_range = 300    # meters

# Dates (Year, Month, Day)
start_date = datetime.datetime(2018, 9, 4)
stop_date = None

# Daily duration threshold (To ignore drive by conditions)
dur_thresh = 2    # hours


##################################################
# Functions
##################################################
def ms_to_datetime(ms):
    return datetime.datetime.fromtimestamp(float(ms) / 1000.0)


def datetime_to_str(dt):
    return dt.strftime("%A %B %d, %Y  %I:%M:%S %p")


def datetime_date_to_str(dt):
    return dt.date().strftime("%Y-%m-%d")


def timedelta_to_hours(td):
    return td.seconds/(60*60)


##################################################
# Main Code
##################################################
if stop_date is None:
    stop_date = datetime.datetime.now()

start_date_ms = int(round(start_date.timestamp() * 1000))
stop_date_ms = int(round(stop_date.timestamp() * 1000))

work_waypoint = (work_lat, work_lon)

# Read in JSON location history file
print("Loading location history (this may take several minutes)")
with open(location_history_file, "r") as read_file:
    location_history = json.load(read_file)

num_locs = len(location_history["locations"])
print("Number of way points to process: " + str(num_locs))

at_work = False
time_start = start_date
loc_ctr = 1
work_log = {}

# Search every entry for proximity to work
for entry in location_history["locations"]:
    # Print progress as this takes a long time
    print(' Processing way point {}/{}\r'.format(loc_ctr, num_locs), end="")
    loc_ctr += 1

    # Skip entry if not within range
    if not start_date_ms <= int(entry["timestampMs"]) <= stop_date_ms:
        continue

    # Convert entry way point to be compatible with geopy
    entry_waypoint = (entry["latitudeE7"]/1e7, entry["longitudeE7"]/1e7)

    # Compute the distance between work and the way point
    distance_m = geodesic(work_waypoint, entry_waypoint).meters

    # Adjust the range considered to be "at work" depending on location accuracy
    try:
        work_range_adj = work_range + entry["accuracy"]

    # If no accuracy reported, just use default range
    except KeyError:
        work_range_adj = work_range

    # Get the time of the entry
    entry_time = ms_to_datetime(entry["timestampMs"])

    # If we are within adjusted range and NOT already at work
    if distance_m <= work_range_adj and not at_work:
        time_start = ms_to_datetime(entry["timestampMs"])
        at_work = True

    # If we are at work but the day has lapsed
    elif time_start.date() != entry_time.date() and at_work:
        # Compute the duration as a difference
        duration = entry_time - time_start
        time_start = entry_time

        # Attempt to add to current date's key
        try:
            work_log[datetime_date_to_str(time_start)] += timedelta_to_hours(duration)

        # If key error, set initial key value
        except KeyError:
            work_log[datetime_date_to_str(time_start)] = timedelta_to_hours(duration)

    # If we were at work and now have left
    elif distance_m > work_range_adj and at_work:
        # Compute the duration as a difference
        duration = entry_time - time_start

        # Attempt to add to current date's key
        try:
            work_log[datetime_date_to_str(time_start)] += timedelta_to_hours(duration)

        # If key error, set initial key value
        except KeyError:
            work_log[datetime_date_to_str(time_start)] = timedelta_to_hours(duration)

        # End time at work
        at_work = False


# Find all days below minimum threshold
del_list = []
for day in work_log:
    if work_log[day] < dur_thresh:
        del_list.append(day)

# Delete minimum days
for day in del_list:
    del work_log[day]

weekday_hours = []
weekend_hours = []
for day in work_log:
    # Weekdays are (monday)0-4 Weekends are 5 and 6(sunday)
    if datetime.datetime.strptime(day, "%Y-%m-%d").weekday() < 5:
        weekday_hours.append(work_log[day])
    else:
        weekend_hours.append(work_log[day])

hours = work_log.values()

# When all is done, print daily hours
print()
print()
print("Between {} and {}: ".format(datetime_date_to_str(start_date), datetime_date_to_str(stop_date)))
print("  Average: {:.2f} hours over {} days".format(statistics.mean(hours), len(work_log)))
print("  Std Dev: {:.2f} hours over {} days".format(statistics.stdev(hours), len(work_log)))

print("  Average weekDAY: {:.2f} hours over {} days".format(statistics.mean(weekday_hours), len(weekday_hours)))
print("  Average weekEND: {:.2f} hours over {} days".format(statistics.mean(weekend_hours), len(weekend_hours)))

min_key = min(work_log, key=work_log.get)
print("  Min: {:.2f} hours on {}".format(work_log[min_key], min_key))

max_key = max(work_log, key=work_log.get)
print("  Max: {:.2f} hours on {}".format(work_log[max_key], max_key))
print()
