#!/usr/bin/env python3
from library.camera_vapi import CameraVapi
from library.alarms_vapi import AlarmVapi
from pprint import pprint
def main():
    # Testing new code structure
    camera_api = CameraVapi()
    alarm_api = AlarmVapi()

    cameras = camera_api.get_camera_devices()
    alarms = alarm_api.get_alarm_devices()

    print("Camera IDs")
    pprint(cameras)
    print("\n\nAlarm IDs")
    pprint(alarms)
if __name__ == "__main__":
    main()