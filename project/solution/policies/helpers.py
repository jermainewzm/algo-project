"""Helper function for the dispatch policies so we dont write duplicated code."""

from typing import Dict, List

from simulator.models import Parcel

def group_waiting_by_location(parcel: Dict[str, Parcel]) -> Dict[str, List[str]]:
    """Group the unassigned parcels by delivery location using a hashmap.
    Returns {location_id: [parcel_id, ...]}
    Time Complexity: O(n log n) for sorted(), then O(n) to group the parcels
    Space Complexity: O(n) for the hashmap
    """
    groups = {}

    for parcel_id in sorted(parcel): #sorted() = O(n log n)
        record = parcel[parcel_id]

        if record["vehicle_assigned"] is None:
            loc = record["delivery_location_id"]

            if loc not in groups:
                groups[loc] = []
            groups[loc].append(parcel_id)

    return groups