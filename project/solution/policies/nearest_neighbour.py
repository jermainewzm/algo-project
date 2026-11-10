"""Nearest Neighbour Approach """

from typing import Dict, List
from simulator.models import Parcel, SimulationContext
from solution.policies.helpers import group_waiting_by_location
HUB = "HUB"

def dispatch(parcel: Dict[str, Parcel], context: SimulationContext) -> List[str]:
    """Nearest Neighbour dispatch (Greedy 1 TSP heuristic).

    Treats the town as a complete weighted graph: locations are nodes and
    travel_distance gives edge weights (km, which also equals minutes at 60 km/h).
    Waiting parcels are grouped by location, and the vehicle repeatedly drives
    to the nearest location with waiting parcels, subject to capacity, range
    and return-cutoff constraints. 

    Delivery windows are ignored in this case

    Parameters
    ----------
    parcel : Dict[str, Parcel]
        Snapshot mapping parcel IDs to their details (e.g., arrival_time, size, delivery_location_id).
    context : SimulationContext
        Dictionary containing simulator state and constraints:
        - current_time (float)
        - vehicle_id (int)
        - capacity (float)
        - travel_distance (Dict[str, Dict[str, float]])
        - departure_delay (float)
        - return_cutoff (float)
        - max_trip_distance_km (float)

    Returns
    -------
    List[str]
        An ordered list of parcel ID strings assigned to the vehicle for this trip.

    Overall Time Complexity: O(n log n + L^2) 
    where L is the number of locations and n = number of parcels at the hub
    Since we know that L <= 36 (plus the hub),
    Time Complexity can be simplified to O(n log n)

    Overall Space Complexity: O(n)
    """
    distances = context["travel_distance"]
    departure = context["current_time"] + context["departure_delay"]
    max_distance = context["max_trip_distance_km"]
    cutoff = context["return_cutoff"]

    #Group waiting parcels by location
    groups = group_waiting_by_location(parcel)

    selected_parcels: List[str] = []
    load = 0.0
    travelled = 0.0  # km from the hub to the current location
    location = HUB

    #Each round pops 1 location, so at most L iterations
    #O(L) X O(L) = O(L^2)
    while groups: #we build the van route one stop at a time, ALWAYS picking the closest next stop
        #Find the nearest location
        best = None
        best_dist = None

        #Scan the remaining locations: O(L)
        for destination in groups:
            leg = distances[location][destination]
            round_trip = travelled + leg + distances[destination][HUB]

            #Skip if going to the destination exceeds the max distance or the 6pm return
            if round_trip > max_distance or departure + round_trip > cutoff:
                continue

            if best is None or (leg, destination) < (best_dist, best):
                best, best_dist = destination, leg

        if best is None:
            break

        #Load every parcel at that location that still fits capacity
        added = False
        parcels_at_stop = groups.pop(best) #we get the list of parcels for this stop

        #Each parcel is checked once across all rounds: O(n) total
        for parcel_id in parcels_at_stop:
            size = parcel[parcel_id]["size"]

            if load + size <= context["capacity"]:
                selected_parcels.append(parcel_id)
                load += size
                added = True

        if added:
            travelled += best_dist
            location = best

    return selected_parcels