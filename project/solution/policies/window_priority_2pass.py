"""Earliest Deadline First (EDF) dispatch using a min-heap, with two-pass filling."""

import heapq
from typing import Dict, List

from simulator.models import Parcel, SimulationContext

HUB = "HUB"

def dispatch(parcel: Dict[str, Parcel], context: SimulationContext) -> List[str]:
    """Earliest Deadline First with two-passes, using a min-heap approach.

    Waiting parcels are kept in a min-heap keyed by window end, so the most
    urgent parcels are popped first.
    Pass 1 adds only parcels that will arrive within their window.
    Pass 2 fills leftover space with the remaining parcels, even if late.

    Difference from the baseline: preferred delivery windows are NOT ignored.

    Overall Time Complexity: O(n log n)
    """
    distances = context["travel_distance"]
    departure = context["current_time"] + context["departure_delay"]
    max_distance = context["max_trip_distance_km"]

    # Min-heap using a tuple of (deadline, parcel_id): earliest deadline at the top
    waiting = [
        (record["delivery_window_end"], parcel_id)
        for parcel_id, record in parcel.items()
        if record["vehicle_assigned"] is None
    ]
    heapq.heapify(waiting)  

    route: List[str] = []
    remaining = []  # parcels skipped in pass 1

    load = 0.0
    travelled = 0.0  
    location = HUB

    # Pass 1: only parcels that will arrive within their window
    # T: O(n log n)
    while waiting:
        deadline, parcel_id = heapq.heappop(waiting)
        record = parcel[parcel_id]

        if load + record["size"] > context["capacity"]:
            remaining.append((deadline, parcel_id))
            continue

        destination = record["delivery_location_id"]
        trip_distance = travelled + distances[location][destination]
        round_trip = trip_distance + distances[destination][HUB]
        # At 60 km/h, km also equals travel time in minutes
        if round_trip > max_distance or departure + round_trip > context["return_cutoff"]:
            remaining.append((deadline, parcel_id))
            continue

        arrival = departure + trip_distance
        if not (record["delivery_window_start"] <= arrival <= record["delivery_window_end"]):
            remaining.append((deadline, parcel_id))
            continue

        route.append(parcel_id)
        load += record["size"]
        travelled = trip_distance
        location = destination

    # Pass 2: fill leftover space with parcels skipped in pass 1.
    # remaining is already in deadline order (popped from the heap).
    # T: O(n)
    for deadline, parcel_id in remaining:
        record = parcel[parcel_id]

        if load + record["size"] > context["capacity"]:
            continue

        destination = record["delivery_location_id"]
        trip_distance = travelled + distances[location][destination]
        round_trip = trip_distance + distances[destination][HUB]
        if round_trip > max_distance or departure + round_trip > context["return_cutoff"]:
            continue

        route.append(parcel_id)
        load += record["size"]
        travelled = trip_distance
        location = destination

    return route