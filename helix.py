# DISCLAIMER - I’M NOT A SOFTWARE ENGINEER SO THERE ARE, NO DOUBT, WAY BETTER WAYS TO DO THIS!  
# DON’T JUDGE ME! 😆

# THE PYTHON PACKAGES NECESSARY FOR THIS PROGRAM
import serial
import time
import requests
import json

# ESTABLISHES THE “LISTENING” CONNECTION TO THE SENSOR’S SERIAL PORT
# UPDATE THE INTERFACE NAME IF NECESSARY
ser = serial.Serial('/dev/ttyACM0')
ser.flushInput()

# THE URL WITH HEADERS NECESSARY TO POST THE EVENT TO COMMAND
# PUT IN YOUR ORG ID AND API KEY
url = "https://api.verkada.com/cameras/v1/video_tagging/event?org_id={VERKADA_ORG_ID}"
headers={"x-api-key": "{VERKADA_API_KEY}"}

# THESE TWO LINES ARE OPTIONAL - THEY ESTABLISH THE URL THAT I USE TO LOG THE OUTCOME OF THE HELIX EVENT
PTurl = "https://logs.collector.solarwinds.com/v1/log"
PTheaders = {'Content-Type': 'application/json','Authorization': 'Basic {PAPERTRAIL_PRESHARED_KEY}'}
# END OF OPTIONAL PORTION

#WHILE LOOP
while True:
    Try:
        # CAPTURES THE TIME OF THE READING IN SECONDS
        readTime = int(time.time())
        # CAPTURES DATA FROM THE SERIAL CONNECTION & DECODES IT
        ser_bytes = ser.readline()
        decoded_bytes = int(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
        
        # MY STREET RUNS NORTH/SOUTH; SO A NEGATIVE VALUE IS “NORTH” AND POSITIVE IS “SOUTH”
        # YOU WILL LIKELY NEED TO CHANGE THIS TO FIT YOUR SCENARIO
        if decoded_bytes < 0:
            speed = (decoded_bytes * -1)
            direction = "North"
        else:
            speed = decoded_bytes
            direction = "South"
        
        # IF STATEMENT IGNORING SPEED READINGS LESS THAN 4MPH
        if speed > 4:
            # CONSTRUCT THE HELIX EVENT PAYLOAD WHICH REQUIRES CAMERA ID, TIME IN MILLISECONDS, EVENT TYPE ID AND DATA POINTS (MPH & DIRECTION)
            eventPayload = json.dumps({
                "camera_id": "{VERKADA_CAM_ID}",
                "time_ms": (readTime + 10) * 1000,
                "event_type_uid": "{VERKADA_HELIX_EVENT_ID}",
                    "attributes": {
                        "mph": int(speed),
                        "direction": str(direction)
                    }
            })

            # HTTPS POST THE HELIX EVENT TO COMMAND
            response = requests.request("POST", url, headers=headers, data=eventPayload)

            # THIS SECTION IS ALSO OPTIONAL - IT CAPTURES THE HTTP RESPONSE CODE AND TEXT AND POSTS IT TO PAPERTRAIL AS A RUDIMENTARY MEANS OF MONITORING FOR HTTP FAILURES
            commandResponse = response.status_code
            commandResponseText = response.text
        
            PTpayload = json.dumps({"app": "helixSpeeds", "time": int(time.time()), "httpCode": commandResponse, "httpResponseText": commandResponseText, "speed": speed, "direction": direction})
            requests.request("POST", PTurl, headers=PTheaders, data=PTpayload)
            # END OF OPTIONAL PORTION

    # “GRACEFUL-ISH” TERMINATION IF THERE’S AN EXCEPTION (ERROR) IN THE TRY - IT CLOSES THE SERIAL CONNECTION AND BREAKS THE PROGRAM
    except:
        ser.close()
        break


