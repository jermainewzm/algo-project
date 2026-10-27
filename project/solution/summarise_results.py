import json
import sys

policy = sys.argv[1]   # e.g. baseline

on_time = []
delivery = []
lateness = []

for i in range(1, 21):
    day = f"day_{i:03d}"   # 1 → day_001
    with open(f"results/{policy}/{day}/metrics.json") as f:
        data = json.load(f)

    on_time.append(data["on_time_rate"])
    delivery.append(data["delivery_rate"])
    lateness.append(data["avg_lateness"])

print("Avg on-time rate:", sum(on_time) / 20)
print("Avg delivery rate:", sum(delivery) / 20)
print("Avg lateness:", sum(lateness) / 20)

