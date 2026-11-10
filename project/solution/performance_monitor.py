"""Calculate performance metrics from one simulation run's event log."""

#Chosen Metric: Delivery On-Time Rate: 
import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from simulator.loaders import day_input_paths

def hhmm_to_mins(time):
    hours, mins = time.split(":")
    return int(hours) * 60 + int(mins)

def calculate_metrics(
    parcels: List[Dict[str, str]],
    distances: List[Dict[str, str]],
    config: Dict[str, Any],
    events: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Return a JSON-serializable dictionary for the chosen performance metric.

    parcels and distances are the rows of the day's CSV files, config is the
    contents of config.json, and events are the records from the run's log.
    CSV values are strings, so convert them before calculating. In particular,
    parcel times are "HH:MM" strings while event times are minutes after
    midnight: "17:00" is 17 * 60 = 1020.
    """

    # Build delivery lookup {parcel_id: delivery_time} and count trips
    number_of_trips = 0
    delivered = {}
    first_vehicle_return = 0
    for event in events:
        if event["event_type"] == "hub_departure":
            number_of_trips += 1

        elif event["event_type"] == "delivery":
            delivered[event["parcel_id"]] = event["time"]

        # time 480 (08:00) is the start of the day, not a real return
        elif event["event_type"] == "vehicle_return" and event["time"] > 480:
            if first_vehicle_return == 0:
                first_vehicle_return = event["time"]

    # print(len(delivered)) check number of logged deliveries
    # print(list(delivered.items())[:5])  [('P000089', 545.443), ('P000250', 548.136), ('P000057', 557.1659999999999), ('P000119', 563.743), ('P000310', 563.965)]
    on_time = 0
    late = 0
    early = 0
    undelivered = 0
    total_late_mins = 0

    parcels_by_arrival_hour = {}  # e.g. {"09:00": {"parcels": 62, "on_time": 0, "early": 0, "late": 62, "undelivered": 0}}

    for row in parcels:
        parcel_id = row["parcel_id"]
        start_time = hhmm_to_mins(row["delivery_window_start"])
        end_time = hhmm_to_mins(row["delivery_window_end"])

        arrival_hour = hhmm_to_mins(row["arrival_time"]) // 60
        hour = f"{arrival_hour:02d}:00"   # 9 → "09:00"
        if hour not in parcels_by_arrival_hour:
            parcels_by_arrival_hour[hour] = {"parcels": 0, "on_time": 0, "early": 0, "late": 0, "undelivered": 0}
        parcels_by_arrival_hour[hour]["parcels"] += 1

        if parcel_id not in delivered:
            undelivered += 1
            parcels_by_arrival_hour[hour]["undelivered"] += 1
        else:
            t = delivered[parcel_id]
            if t < start_time:
                early += 1
                parcels_by_arrival_hour[hour]["early"] += 1
            elif t > end_time:
                late += 1
                total_late_mins += t - end_time
                parcels_by_arrival_hour[hour]["late"] += 1
            else:
                on_time += 1
                parcels_by_arrival_hour[hour]["on_time"] += 1

    total = len(parcels)
    
    #We aim to increase on time rate by improving delivery rate and reduce lateness of delivery
    #PRIMARY Metric 1: on_time_rate = on time parcels / all parcels
    on_time_rate = on_time / total

    #SECONDARY Metric 1: delivery rate
    delivery_rate = (on_time + early + late) / total

    #SECONDARY Metric 2: avg lateness
    avg_lateness = total_late_mins / late if late > 0 else 0

    return {
        "on_time_rate" : on_time_rate,
        "delivery_rate" : delivery_rate,
        "avg_lateness": avg_lateness,
        "on_time": on_time,
        "late": late,
        "early": early,
        "undelivered": undelivered,
        "number_of_trips": number_of_trips,
        "first_vehicle_return" : first_vehicle_return,
        "parcels_by_arrival_hour" : parcels_by_arrival_hour
    }

def main(argv: Optional[List[str]] = None) -> int:
    """Load one day's inputs and event log, then write the metrics report."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data"),
                        help="directory containing dist.csv, config.json and demand/")
    parser.add_argument("--day", required=True, help="day identifier, for example day_001")
    parser.add_argument("--log", type=Path, required=True,
                        help="event log from a simulator run")
    parser.add_argument("--output", type=Path,
                        help="JSON report (default: metrics.json beside the selected log)")
    args = parser.parse_args(argv)
    try:
        parcel_path, distance_path, config_path = day_input_paths(args.data, args.day)
        output = args.output if args.output is not None else args.log.with_name("metrics.json")
        # The input files all live in the data directory, so this also protects them.
        if output.resolve() == args.data.resolve() or args.data.resolve() in output.resolve().parents:
            raise ValueError("report output must be outside the input data directory")
        if output.resolve() == args.log.resolve():
            raise ValueError("report output must not overwrite the log")
        with parcel_path.open(newline="", encoding="utf-8-sig") as stream:
            parcels = list(csv.DictReader(stream))
        with distance_path.open(newline="", encoding="utf-8-sig") as stream:
            distances = list(csv.DictReader(stream))
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        with args.log.open(encoding="utf-8") as stream:
            events = [json.loads(line) for line in stream if line.strip()]
        metrics = calculate_metrics(parcels, distances, config, events)
        report = json.dumps(metrics, indent=2, allow_nan=False) + "\n"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(f"Metrics report: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
