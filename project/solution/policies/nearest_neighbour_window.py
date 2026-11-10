"""Window-Aware Nearest Neighbour (WA-NN) Approach. Follows the Nearest Neighbour logic but takes into account the delivery window"""

from typing import Dict, List

from simulator.models import Parcel, SimulationContext
from solution.policies.helpers import group_waiting_by_location

HUB = "HUB"

def dispatch(parcel: Dict[str, Parcel], context: SimulationContext) -> List[str]:
    """Window-Aware Nearest Neighbour.

    Builds the route with Nearest Neighbour but checks each parcel's
    estimated arrival time against its delivery window.

    HOW IT WORKS:
    Pass 1: visit the nearest stop with parcels that would arrive ON TIME.
    Pass 2: fill spare capacity with parcels that would arrive LATE.
    Parcels that would arrive EARLY are left at the hub for a later trip.

    Overall Time Complexity: O(n log n + k * n),
    where n = number of parcels that have arrived at the hub
    and k = number of stops made on this trip.

    A stop can be visited more than once here,
    so k is not limited by the number of locations

    The time complexity is simplified to O(n log n)
    because k <= capacity/ smallest parcel size.

    Overall Space Complexity: O(n)

    groups, loaded_parcels and selected_parcels each hold at most n parcels
    """
    distances = context["travel_distance"]
    departure = context["current_time"] + context["departure_delay"]
    max_distance = context["max_trip_distance_km"]
    cutoff = context["return_cutoff"]

    #Same as nearest neighbour, we group parcels by location
    groups = group_waiting_by_location(parcel)
    
    selected_parcels: List[str] = []
    load = 0.0
    loaded_parcels = set()  #set lookup is O(1)
    travelled = 0.0  # km from the hub to the current location
    location = HUB

    #note: Early parcels wont be loaded so they can wait at the hub for a later trip
    #Pass 1: we only load parcels on-time.
    #Each round scans all waiting parcels. T: O(n),
    #and each round adds one stop, so k rounds T: O(k * n)
    while True:
        best = None
        best_dist = None
        best_parcels = None

        for destination in groups:
            leg = distances[location][destination]
            round_trip = travelled + leg + distances[destination][HUB]

            #skip if going to the destinaton exceeds the max distance or the 6pm return
            if round_trip > max_distance or departure + round_trip > cutoff:
                continue

            arrival = departure + travelled + leg #at 60 km/h, km = minutes

            #we need to decide per parcel, since parcels at the same stop can have different windows

            eligible = []
            for parcel_id in groups[destination]:
                if parcel_id in loaded_parcels:
                    continue
                start = parcel[parcel_id]["delivery_window_start"]
                end = parcel[parcel_id]["delivery_window_end"]

                if start <= arrival <= end: #on time
                    eligible.append(parcel_id)

            if not eligible:
                continue

            if best is None or (leg, destination) < (best_dist, best):
                best, best_dist, best_parcels = destination, leg, eligible

        if best is None:
            break  #no reachable stop with on-time parcels 

        added = False

        for parcel_id in best_parcels:
            size = parcel[parcel_id]["size"]

            if load + size <= context["capacity"]:
                selected_parcels.append(parcel_id)
                loaded_parcels.add(parcel_id)
                load += size
                added = True

        if not added:
            break #van is full

        travelled += best_dist
        location = best

    #Pass 2: late parcels are loaded to fill spare capacity
    #Here,same cost as pass 1: T: O(n) per round, one stop added per round

    while True:
        best = None
        best_dist = None
        best_parcels = None

        for destination in groups:
            leg = distances[location][destination]
            round_trip = travelled + leg + distances[destination][HUB]

            #again, skip if going to the destination exceeds the max distance or 6pm return
            if round_trip > max_distance or departure + round_trip > cutoff:
                continue

            arrival = departure + travelled + leg

            eligible = []

            for parcel_id in groups[destination]:
                if parcel_id in loaded_parcels:
                    continue
                end = parcel[parcel_id]["delivery_window_end"]

                if arrival > end: #this parcel is going to be late
                    eligible.append(parcel_id)

            if not eligible:
                continue

            if best is None or (leg, destination) < (best_dist, best):
                best, best_dist, best_parcels = destination, leg, eligible

        if best is None:
            break

        added = False
        for parcel_id in best_parcels:
            size = parcel[parcel_id]["size"]

            if load + size <= context["capacity"]:
                selected_parcels.append(parcel_id)
                loaded_parcels.add(parcel_id)
                load += size
                added = True

        if not added:
            break #van is full already
        travelled += best_dist
        location = best

    return selected_parcels




    




