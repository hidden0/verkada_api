#!/usr/bin/env python3
import sys
import os
# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import serial
import time
from pprint import pprint
from library.vapi import Vapi

SPEEDING = 25

def connect_to_serial():
    for i in range(10):  # Try /dev/ttyACM0 to /dev/ttyACM9
        try:
            device_name = f"/dev/ttyACM{i}"
            ser = serial.Serial(device_name)
            ser.flushInput()
            print(f"Connected to {device_name}")
            return ser
        except serial.SerialException:
            print(f"Failed to connect to {device_name}")
    raise Exception("Unable to connect to any serial device")

def format_helix_and_post_event(vapi, org_id, camera_id, event_type_uid, direction, velocity):
    new_direction = "East" if direction == "inbound" else "West"
    read_time = int(time.time() * 1000)  # Convert to milliseconds
    attributes = {
        "direction": new_direction,
        "mph": velocity
    }
    post_event(vapi, org_id, camera_id, attributes, read_time, event_type_uid)

def post_event(vapi, org_id, camera_id, attributes, time_ms, event_type_uid):
    response = vapi.post_helix_event(
        org_id=org_id,
        camera_id=camera_id,
        attributes=attributes,
        time_ms=time_ms,
        event_type_uid=event_type_uid,
    )
    pprint(response)

def parse_radar_data(vapi, org_id, camera_id, event_type_uid, data):
    try:
        json_data = json.loads(data)
        direction = json_data.get("direction")
        velocity = abs(int(json_data.get("DetectedObjectVelocity", 0)))
        print(f"Direction: {direction}, Velocity: {velocity}")
        if velocity > SPEEDING:
            format_helix_and_post_event(vapi, org_id, camera_id, event_type_uid, direction, velocity)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON: {data}")

def main():
    # Initialize the Vapi instance
    vapi = Vapi()
    # Define camera and organization IDs
    org_id = "48684ea6-d592-436f-a282-5f6aad829d06"
    camera_id = "663c5bbf-e033-40fb-b9f5-e0437560840f"
    event_type_id = "a4cde31e-e984-4fcc-a026-dbd5c80d13e8"

    # Connect to the serial device
    ser = connect_to_serial()

    # Main loop to read and process radar data
    while True:
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                parse_radar_data(vapi, org_id, camera_id, event_type_id, data)
            time.sleep(0.1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)  # Add delay to prevent high CPU usage

if __name__ == "__main__":
    main()
