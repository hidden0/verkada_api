#!/usr/bin/env python3
import sys
import os
# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import time
from pprint import pprint
from library.helix_vapi import HelixVapi


def main():
    # Initialize the Vapi instance
    vapi = HelixVapi()
    # Define camera and organization IDs
    org_id = "cbe2df58-36fd-46f3-9148-e300bbee8489"
    #camera_id = "1ac0a065-7044-46e0-97eb-0664dab72e0d"
    camera_id = "39cbf5dd-e5b7-47f6-bc2c-cffc36d8df91"
    event_type_id = "8a16d96a-a4d6-4d6e-bbd6-8d1435c824c2"
    attributes = {
        "isCool": True
    }
    read_time = int(time.time() * 1000)  # Convert to milliseconds
    print(vapi.api_key)
    response = vapi.create_helix_event(camera_id, attributes, read_time, event_type_id, org_id)
    print(response)
if __name__ == "__main__":
    main()
