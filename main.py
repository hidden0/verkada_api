#!/usr/bin/env python3
#imports
from datetime import timezone
from pprint import pprint
from library.vapi import Vapi
from datetime import datetime, timedelta

def main():
    # Initialize the Vapi instance
    vapi = Vapi()

    # Define camera and organization IDs
    org_id = "48684ea6-d592-436f-a282-5f6aad829d06"
    camera_id = "663c5bbf-e033-40fb-b9f5-e0437560840f"

    # Calculate the start and end times for the last hour
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=5)

    # Get historic footage
    #vapi.get_historic_footage(camera_id, org_id, start_time, end_time, "6")
    #vapi.download_all_cameras(org_id, start_time, end_time)

if __name__ == "__main__":
    main()