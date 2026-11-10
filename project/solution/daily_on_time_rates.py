import json

# The five policies to compare (same names as the folders in results/)
policies = [
    "baseline",
    "window_priority_1pass",
    "window_priority_2pass",
    "nearest_neighbour",
    "nearest_neighbour_window",
]

# Print the column names once, at the top
print("day      baseline  EDF-1pass  EDF-2pass  NN  WA-NN   (on-time rate in %)")

# Go through the 20 days one at a time
for i in range(1, 21):
    day = f"day_{i:03d}"   # 1 → day_001

    # Start the row with the day, then add one number per policy
    row = day

    for policy in policies:
        with open(f"results/{policy}/{day}/metrics.json") as f:
            data = json.load(f)

        on_time_percent = data["on_time_rate"] * 100   # e.g. 0.817 → 81.7
        row = row + "  " + str(round(on_time_percent, 1))

    print(row)