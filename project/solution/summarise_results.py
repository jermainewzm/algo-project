import json
import sys

policy = sys.argv[1]   # e.g. baseline

on_time = []
delivery = []
lateness = []
early = []
late = []
undelivered = []
trips = []

for i in range(1, 21):
    day = f"day_{i:03d}"   # 1 → day_001
    with open(f"results/{policy}/{day}/metrics.json") as f:
        data = json.load(f)

    on_time.append(data["on_time_rate"])

    delivery.append(data["delivery_rate"])

    lateness.append(data["avg_lateness"])

    early.append(data["early"])

    late.append(data["late"])

    undelivered.append(data["undelivered"])
    
    trips.append(data["number_of_trips"])

print("Avg on-time rate:", sum(on_time) / 20)
print("Avg delivery rate:", sum(delivery) / 20)
print("Avg lateness:", sum(lateness) / 20)
print("Avg early parcels:", sum(early) / 20)
print("Avg late parcels:", sum(late) / 20)
print("Avg undelivered parcels:", sum(undelivered) / 20)
print("Avg trips:", sum(trips) / 20)