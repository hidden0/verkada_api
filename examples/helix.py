#!/usr/bin/env python3
import sys
import os
# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#imports
from datetime import timezone, datetime, timedelta
from pprint import pprint
from library.vapi import Vapi
import json
import serial
import time

SPEEDING = 25
class Helix:
    def __init__(self, org_id, camera_id, event_type_uid):
        for i in range(10):  # Try /dev/ttyACM0 to /dev/ttyACM9
            try:
                device_name = f"/dev/ttyACM{i}"
                self.ser = serial.Serial(device_name)
                self.ser.flushInput()
                print(f"Connected to {device_name}")
                break
            except serial.SerialException:
                print(f"Failed to connect to {device_name}")

        if self.ser is None:
            raise Exception("Unable to connect to any serial device")
        self.vapi = Vapi()
        self.org_id = org_id
        self.camera_id = camera_id
        self.event_type_uid = event_type_uid
        self.attributes = None

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
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode('utf-8').strip()
                    self.parse_radar_data(data)
                time.sleep(0.1)

            except Exception as e:
                print(f"Error: {e}")
            time.sleep(1)  # Add delay to prevent high CPU usage
    def parse_radar_data(self, data):
        try:
            json_data = json.loads(data)
            direction = json_data.get("direction")
            velocity = int(json_data.get("DetectedObjectVelocity"))
            print(f"Direction: {direction}, Velocity: {velocity}")
            if(velocity>SPEEDING):
                dir = None
                if(direction=="inbound"):
                    dir = "East"
                else:
                    dir = "West"
                read_time = int(time.time() * 1000)  # Convert to milliseconds
                self.attributes = {
                    "direction": dir,
                    "mph": velocity
                }
                self.vapi.post_helix_event(self.camera_id, self.attributes, read_time, self.event_type_uid, self.org_id)
            
        except json.JSONDecodeError:
            print(f"Failed to decode JSON: {data}")


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
