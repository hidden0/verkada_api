#!/usr/bin/env python3
#imports
from datetime import timezone
from pprint import pprint
from library.vapi import Vapi
from datetime import timedelta
from time import time

def main():
    # Initialize the Vapi instance
    vapi = Vapi()
    # Test helix
    camera_id = "663c5bbf-e033-40fb-b9f5-e0437560840f"
    event_type_id = "a4cde31e-e984-4fcc-a026-dbd5c80d13e8"
    attributes = {
        "mph": 2,
        "direction": "Up"        
    }
    current_time_ms = int(time() * 1000)
    print(f"{current_time_ms}")
    pprint(vapi.post_helix_event(camera_id, attributes=attributes, time_ms=current_time_ms, event_type_uid=event_type_id))

if __name__ == "__main__":
    main()