import json
import sys

policy = sys.argv[1]  

parcels = {}   # arrival hour -> parcels over the 20 days
on_time = {}     # arrival hour -> parcels delivered on time
early = {}     # arrival hour -> parcels delivered early
earliest_return = None   # earliest time any vehicle came back, over the 20 days

for i in range(1, 21):
    day = f"day_{i:03d}"   # 1 → day_001
    with open(f"results/{policy}/{day}/metrics.json") as f:
        data = json.load(f)

    # Add this day's counts to the running totals for each arrival hour
    for hour in data["parcels_by_arrival_hour"]:
        counts = data["parcels_by_arrival_hour"][hour]

        if hour not in parcels:
            parcels[hour] = 0
            on_time[hour] = 0
            early[hour] = 0

        parcels[hour] += counts["parcels"]
        on_time[hour] += counts["on_time"]
        early[hour] += counts["early"]

    if earliest_return is None or data["first_vehicle_return"] < earliest_return:
        earliest_return = data["first_vehicle_return"]

# One line per arrival hour
for hour in sorted(parcels):
    on_time_percent = 100 * on_time[hour] / parcels[hour]
    print("Arrive", hour, "-",
          round(parcels[hour] / 20), "parcels/day,",
          round(on_time_percent, 1), "% on time,",
          round(early[hour] / 20), "early/day")

hours = int(earliest_return) // 60
mins = int(earliest_return) % 60
print(f"Earliest vehicle return: {hours:02d}:{mins:02d}")