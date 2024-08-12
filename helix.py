#!/usr/bin/env python3
# Let's refactor helix.py using the Vapi structure from vapi.py.
#imports
from datetime import timezone, datetime, timedelta
from pprint import pprint
from library.vapi import Vapi
import json
import serial
import time
class Helix:
    def __init__(self, org_id, camera_id, event_type_uid):
        self.ser = serial.Serial("/dev/ttyACM0")
        self.ser.flushInput()
        self.vapi = Vapi()
        self.org_id = org_id
        self.camera_id = camera_id
        self.event_type_uid = event_type_uid

    def post_event(self, attributes, time_ms):  
        response = self.vapi.post_helix_event(
            org_id=self.org_id,
            camera_id=self.camera_id,
            attributes=attributes,
            time_ms=time_ms,
            event_type_uid=self.event_type_uid
        )
        return response 
    def run(self):
        while True:
            try:
                read_time = int(time.time() * 1000)  # Convert to milliseconds
                if self.ser.in_waiting > 0:
                    sensor_data = self.ser.readline().decode("utf-8").rstrip()
                    attributes = None
                    if(int(sensor_data)>0):
                        attributes = { "mph": sensor_data,
                                     "direction": "East" }
                        print(f"MPH: {sensor_data} and Direction East")
                    else:
                        attributes = { "mph": sensor_data*-1,
                                     "direction": "West" }
                        print(f"MPH: {sensor_data} and Direction West")
                    response = self.post_event(attributes, read_time)
                    print(f"Event Posted: {response.status_code}")
                    log_data = {"timestamp": read_time, "response_code": response.status_code}

            except Exception as e:
                print(f"Error: {e}")
            time.sleep(1)  # Add delay to prevent high CPU usage



def main():
    # Initialize the Vapi instance
    # Define camera and organization IDs
    org_id = "48684ea6-d592-436f-a282-5f6aad829d06"
    camera_id = "663c5bbf-e033-40fb-b9f5-e0437560840f"
    event_type_id = "a4cde31e-e984-4fcc-a026-dbd5c80d13e8"
    # Initialize the Helix instance
    helix_event = Helix(org_id, camera_id, event_type_id)
    helix_event.run()

if __name__ == "__main__":
    main()