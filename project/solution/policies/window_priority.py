"""First Approach: Earlest Deadline First"""

from typing import Dict, List

from simulator.models import Parcel, SimulationContext

HUB = "HUB"

def dispatch(parcel: Dict[str, Parcel], context: SimulationContext) -> List[str]:
    """Earliest Deadline First with two-pass filling.

    To do this, we first sort the parcels by window end, so the most urgent parcels get loaded first.
    Pass 1 adds only parcels that will arrive within their window.
    Pass 2 fills leftover space with the remaining parcels even if they are late.
    
    Difference with baseline approach: preferred window is NOT ignored
    """
    distances = context["travel_distance"]
    departure = context["current_time"] + context["departure_delay"]
    max_distance = context["max_trip_distance_km"]

    # Earliest deadline first
    waiting = sorted(
        (parcel_id for parcel_id, record in parcel.items() if record["vehicle_assigned"] is None),
        key=lambda parcel_id: (parcel[parcel_id]["delivery_window_end"], parcel_id),
    )

    route: List[str] = []
    chosen = set()  # parcels already in the route, lookup is only O(1)
    load = 0.0
    travelled = 0.0  # km from the hub to the route's last stop
    location = HUB

    # Pass 1: only parcels that will arrive within their window T: O(n)
    for parcel_id in waiting:
        record = parcel[parcel_id]
        if load + record["size"] > context["capacity"]:
            continue
        destination = record["delivery_location_id"]
        trip_distance = travelled + distances[location][destination]
        round_trip = trip_distance + distances[destination][HUB]
        # At 60 km/h, km also equals travel time in minutes
        if round_trip > max_distance or departure + round_trip > context["return_cutoff"]:
            continue
        arrival = departure + trip_distance
        if not (record["delivery_window_start"] <= arrival <= record["delivery_window_end"]):
            continue
        route.append(parcel_id)
        chosen.add(parcel_id)
        load += record["size"]
        travelled = trip_distance
        location = destination

    # Pass 2: fill leftover space with the remaining parcels T: O(n) since set lookup is O(1)
    for parcel_id in waiting:
        if parcel_id in chosen:
            continue
        record = parcel[parcel_id]
        if load + record["size"] > context["capacity"]:
            continue
        destination = record["delivery_location_id"]
        trip_distance = travelled + distances[location][destination]
        round_trip = trip_distance + distances[destination][HUB]
        if round_trip > max_distance or departure + round_trip > context["return_cutoff"]:
            continue
        route.append(parcel_id)
        chosen.add(parcel_id)
        load += record["size"]
        travelled = trip_distance
        location = destination

    return route