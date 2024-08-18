#!/usr/bin/env python3
import sys
import os
# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library.helix_vapi import HelixVapi
from pprint import pprint

helix_api = HelixVapi()

def delete_low_speed_events(min_speed=30):
    """
    Deletes Helix events where the speed (mph) is less than the specified minimum speed.

    Args:
        min_speed (int): The minimum speed threshold. Events with speeds below this threshold will be deleted.
    """
    event_count = 0
    # Search for all Helix events
    response = helix_api.search_helix_events()
    events = response.json()
    for event in events.get("events", []):
        # Extract the mph value from the event attributes
        mph = event["attributes"].get("mph")
        # Check if the mph value is below the minimum speed
        if mph is not None and mph < min_speed:
            # Extract necessary identifiers for deletion
            camera_id = event.get("camera_id")
            event_time_ms = event.get("time_ms")
            event_uid = event.get("event_type_uid")

            # Perform deletion
            if camera_id and event_time_ms and event_uid:
                response = helix_api.delete_helix_event(camera_id, event_time_ms, event_uid)
                print(f"Deleted event {event_uid} at time {event_time_ms} with speed {mph} mph from camera {camera_id}")
                event_count += 1
    print(f"Deleted {event_count} events total.")

if __name__ == "__main__":
    delete_low_speed_events(min_speed=30)   