"""
Description:
    Class Object Definition file for Verkada API interaction.

Author:
    John Thorne
"""


""" Imports """
import configparser
import sys
import os
import requests
from library.utils import colors as col
import library.utils as utils
from datetime import datetime, timedelta
import json
import subprocess
import time
import threading
from tqdm import tqdm

# TODO Add ability to load different config files

# Constants
API_VERSION = "v1"
## Products
PRODUCT_CAMERA = "cameras"
PRODUCT_CORE = "core"
PRODUCT_ACCESS = "access"
PRODUCT_SENSOR = "environment"
PRODUCT_GUEST = "guest"
PRODUCT_ALARMS = "alarms"
PRODUCT_EVENTS = "events"

## Endpoint Constants - Cameras
EP_CAMERA_DEVICES = f"{PRODUCT_CAMERA}/{API_VERSION}/devices"

## Streaming
EP_CAMERA_FOOTAGE_TOKEN = f"{PRODUCT_CAMERA}/{API_VERSION}/footage/token"

## Endpoint Constants - Alarms
EP_ALARM_DEVICES = f"{PRODUCT_ALARMS}/{API_VERSION}/devices"
EP_ALARM_SITES = f"{PRODUCT_ALARMS}/{API_VERSION}/sites"

## Endpoint Constants - Helix
EP_HELIX = f"{PRODUCT_CAMERA}/{API_VERSION}/video_tagging/event"

"""
Vapi class for handling API key initialization, configuration loading, HTTP error handling, and device data retrieval.

Returns:
    None
"""
class Vapi:
    # Constants and default values
    API_KEY = None
    STREAMING_API_KEY = None
    API_URL = None
    API_KEY_VALID = False
    ORG_ID = None

    # Fields of the API call itself
    API_ENDPOINT = None
    API_ENDPOINT_PARAMS = None

    # Fields to hold config file items
    API_ENV_VAR_NAME = None
    API_DEFAULT_CRED_FILE = None
    API_DEFAULT_STREAMING_CRED_FILE = None
    
    # Misc fields
    API_KEY_METHOD = None
    """
    Initialize the VAPI class with the option to run a test on the API key.

    Args:
        run_test (bool): Flag to indicate whether to run a test on the API key. Defaults to True.

    Returns:
        None
    """
    def __init__(self, run_test=True):
        self.API_KEY = None 
        self.STREAMING_API_KEY = None
        self.API_KEY_METHOD = None

        # Load the config
        self.load_config()

        # First, load the regular API key
        self.API_KEY = self.load_api_key(
            env_var="VERKADA_API_KEY",
            cred_file=self.API_DEFAULT_CRED_FILE,
            key_type="API"
        )

        # Then, load the streaming API key
        self.STREAMING_API_KEY = self.load_api_key(
            env_var="VERKADA_STREAMING_API_KEY",
            cred_file="stream_api.cred",  # Assuming you have this in your config or defined elsewhere
            key_type="Streaming API"
        )

        # Validate the regular API key if run_test is True
        if run_test and self.API_KEY:
            self.key_test(self.API_KEY)

    def load_api_key(self, env_var, cred_file, key_type):

        """Helper method to load an API key from an environment variable, command line, or a credentials file."""
        temp_api_key = None

        # Try to load the key from a command-line argument
        try:
            temp_api_key = sys.argv[1]
            self.API_KEY_METHOD = f"{key_type} from CLI"
        except IndexError:
            # Next, try to load the key from an environment variable
            temp_api_key = os.getenv(env_var)
            if temp_api_key:
                self.API_KEY_METHOD = f"{key_type} from ENV"
            else:
                # Finally, try to load the key from a credentials file
                try:
                    with open(cred_file, "r") as f:
                        temp_api_key = f.read().strip()
                        self.API_KEY_METHOD = f"{key_type} from CRED File"
                except FileNotFoundError as e:
                    col.print_error(e)

        # If no key is found, prompt the user for input
        if temp_api_key is None:
            temp_api_key = input(f"Please enter your {key_type} key: ")
            self.API_KEY_METHOD = f"{key_type} from INPUT"

        return temp_api_key
    
    def send_request(self, api_key=None, endpoint=None, params=None):
        print(endpoint)
        try:
            if api_key is None:
                api_key = self.API_KEY
            headers = {
                "accept": "application/json",
                "x-api-key": api_key
            }
            url = f"{self.API_URL}/{endpoint}"
            return requests.get(url, headers=headers, params=params)
        except Exception:
            self.handle_http_errors(
                    0,
                    f"{self.API_URL}/{endpoint}",
                    self.API_KEY,
                )
    
    def send_streaming_request(self, endpoint, params=None):
        headers = {
            "accept": "application/json",
            "x-api-key": self.STREAMING_API_KEY
        }
        url = f"{self.API_URL}/{endpoint}"
        return requests.get(url, headers=headers, params=params)
    
    # TODO [] Generate streaming API key test
    def key_test(self, key):
        # Make sure the key is the right length and format
        try:
            if len(key) != 40:
                raise utils.InvalidAPIKeyLength(len(key))
            if not key.startswith("vkd_api_"):
                raise utils.InvalidAPIKeyFormat()
        except Exception as e:
            print(f"Error: {e.message}")

        # Make sure the key is usable
        # Test API against the AUDIT log which should always be reachable
        try:
            response = self.send_request(api_key=key, endpoint="core/v1/audit_log?page_size=100")
            if response.status_code == 200:
                self.API_KEY = key
                return 0
            else:
                self.handle_http_errors(response.status_code, "core/v1/audit_log?page_size=100", self.API_KEY)
            print(f"Key tested successfully: {key}")
        except Exception as e:
            col.print_error(e.message)
            exit(e.code)
    """
    Fetches and returns alarm site IDs.

    Returns:
    list: A list of site IDs.
    """
    def get_alarm_site_ids(self):
        # TODO [] Get rid of invalid sites 
        invalid_site_id = "e71edc44-f20e-4893-b6d2-c03f41b9e83a"  # The site ID to skip
        try:
            response = self.send_request(endpoint=EP_ALARM_SITES)

            if response.status_code == 200:
                data = response.json()
                sites = data.get('sites', [])
                return [
                    site['site_id']
                    for site in sites
                    if site['site_id'] != invalid_site_id
                ]
            else:
                self.handle_http_errors(
                    response.status_code,
                    f"{self.API_URL}/{EP_ALARM_SITES}",
                    self.API_KEY,
                )

        except utils.BaseAPIException as e:
            col.print_error(e)
            sys.exit(e.code)
    """
    Fetch alarm IDs associated with the alarms for each site and store them with the product information.

    Returns:
        dict: A dictionary containing alarm IDs mapped to their product information.
    """
    def get_alarm_ids(self):
        # Fetch site IDs for alarms and pass as query parameters
        alarm_ids = {}
        site_ids = self.get_alarm_site_ids()
        for site_id in site_ids:
            params = {'site_id': site_id}
            response = self.send_request(endpoint=EP_ALARM_DEVICES, params=params)
            if response.status_code == 200:
                data = response.json()
                for device in data.get("devices", []):
                    if device_id := device.get("device_id"):
                        alarm_ids[device_id] = {"product": PRODUCT_ALARMS}
            else:
                self.handle_http_errors(
                    response.status_code,
                    f"{self.API_URL}/{EP_ALARM_DEVICES}",
                    self.API_KEY,
                )
        return alarm_ids
    def get_camera_ids(self):
        camera_ids = {}
        response = self.send_request(endpoint=EP_CAMERA_DEVICES)
        if response.status_code == 200:
            data = response.json()
            for camera in data.get("cameras", []):
                if camera_id := camera.get("camera_id"):
                    camera_ids[camera_id] = {"product": "camera"}
        else:
            self.handle_http_errors(
                response.status_code,
                f"{self.API_URL}/{EP_CAMERA_DEVICES}",
                self.API_KEY,
            )
        return camera_ids
    """
    Retrieve device IDs based on the specified product.

    Args:
        product (str): The product for which to retrieve device IDs. Defaults to "all".

    Returns:
        dict: A dictionary containing device IDs mapped to device information.
    """
    def get_device_ids(self, product="all"):
        valid_products = {
            PRODUCT_CAMERA: EP_CAMERA_DEVICES,
            PRODUCT_ALARMS: EP_ALARM_DEVICES,
            # Add other products with devices endpoints here
        }

        if product == "all":
            products_to_fetch = valid_products.keys()
        else:
            products_to_fetch = [product.lower()]
            if products_to_fetch[0] not in valid_products:
                print(f"Invalid product: {product}")
                return {}

        try:
            device_ids = {}
            for prod in products_to_fetch:
                if prod == PRODUCT_ALARMS:
                    # Fetch site IDs for alarms and pass as query parameters
                    device_ids |= self.get_alarm_ids()
                elif prod == PRODUCT_CAMERA:
                    device_ids |= self.get_camera_ids()

            return device_ids
        except utils.BaseAPIException as e:
            col.print_error(e)
            sys.exit(e.code)
    """
    Load configuration settings from a specified file and assign them to class attributes.

    Args:
        config_file (str): The path to the configuration file. Defaults to "config.ini".

    Raises:
        FailedConfigLoad: If the specified configuration file does not exist.

    Returns:
        None
    """
    def load_config(self, config_file="config.ini"):
        try:
            if not os.path.exists(config_file):
                raise utils.FailedConfigLoad()

            # Load the API configuration
            config = configparser.ConfigParser()

            # Load the configuration file
            config.read(config_file)

            # Access the configuration values
            self.API_URL = config['DEFAULT']['api_url']
            self.API_DEFAULT_CRED_FILE = config['DEFAULT']['API_DEFAULT_CREDENTIALS_FILE']
            self.API_DEFAULT_STREAMING_CRED_FILE = config['DEFAULT']['API_DEFAULT_STREAMING_CREDENTIALS_FILE']
            self.API_ENV_VAR_NAME = config['DEFAULT']['API_ENVIRONMENT_VARIABLE']
            self.API_STREAMING_ENVIRONMENT_VAR_NAME= config['DEFAULT']['API_STREAMING_ENVIRONMENT_VARIABLE']
            self.ORG_ID = config['DEFAULT']['ORG_ID']

        except Exception as e:
            print(f"Error: {str(e)}")
    """
    Handle HTTP errors based on the provided status code.

    Args:
        status_code (int): The HTTP status code to handle.

    Returns:
        None

    Raises:
        ClientErrorBadRequest: If the status code is 400.
        ClientErrorUnauthorized: If the status code is 401.
        ClientErrorForbidden: If the status code is 403.
        ClientErrorNotFound: If the status code is 404.
        ClientErrorTooManyRequests: If the status code is 429.
        ServerErrorInternal: If the status code is 500.
    """
    def handle_http_errors(self, status_code, endpoint, key):
        if status_code == 400:
            raise utils.ClientErrorBadRequest(endpoint=endpoint, api_key=key)
        elif status_code == 401:
            raise utils.ClientErrorUnauthorized(endpoint=endpoint, api_key=key)
        elif status_code == 403:
            raise utils.ClientErrorForbidden(endpoint=endpoint, api_key=key)
        elif status_code == 404:
            raise utils.ClientErrorNotFound(endpoint=endpoint, api_key=key)
        elif status_code == 429:
            raise utils.ClientErrorTooManyRequests(endpoint=endpoint, api_key=key)
        elif status_code == 500:
            raise utils.ServerErrorInternal(endpoint=endpoint, api_key=key)
    """
    Filters the device dictionary by product type.

    Args:
        device_dict (dict): The dictionary containing device information.
        product_type (str): The product type to filter by (e.g., "cameras", "alarms").

    Returns:
        dict: A dictionary filtered by the specified product type.
    """
    def filter_by_product_type(self, device_dict, product_type):
        
        return {device_id: details for device_id, details in device_dict.items() if details['product'] == product_type}
    
    def get_stream_token(self, TTL=3600):
        token_file = "stream_token.cred"
        
        # Check if token exists and is still valid
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                token_data = json.load(f)
                token = token_data.get("token")
                timestamp = datetime.fromisoformat(token_data.get("timestamp"))

                # Check if the token is still valid
                if datetime.now() - timestamp < timedelta(seconds=TTL):
                    return token

        # If no valid token, fetch a new one
        response = self.send_streaming_request(endpoint=EP_CAMERA_FOOTAGE_TOKEN, params={"expiration": TTL})

        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("jwt")

            # Store the token with the current timestamp
            with open(token_file, 'w') as f:
                json.dump({"token": token, "timestamp": datetime.now().isoformat()}, f)

            return token
        else:
            self.handle_http_errors(response.status_code, EP_CAMERA_FOOTAGE_TOKEN, self.API_KEY)
            return None

    def get_historic_footage_chunk(self, camera_id, org_id, chunk_start, chunk_end, chunk_num, semaphore, position):
        with semaphore:
            token = self.get_stream_token()
            if not token:
                return

            start_time_epoch = int(chunk_start.timestamp())
            end_time_epoch = int(chunk_end.timestamp())
            base_url = "https://api.verkada.com/stream/cameras/v1/footage/stream/stream.m3u8"
            params = {
                "camera_id": camera_id,
                "org_id": org_id,
                "start_time": start_time_epoch,
                "end_time": end_time_epoch,
                "resolution": "high_res",
                "jwt": token
            }
            response = requests.Request('GET', base_url, params=params).prepare()
            final_url = response.url

            total_duration = end_time_epoch - start_time_epoch
            video_folder = "video"
            os.makedirs(video_folder, exist_ok=True)
            chunk_output_file = os.path.join(video_folder, f"{camera_id}_chunk_{chunk_num}.mp4")

            pbar = tqdm(total=total_duration, desc=f"Camera {camera_id} Chunk {chunk_num}", position=position, leave=True)

            try:
                self.download_footage_from_m3u8(final_url, total_duration, camera_id, pbar, chunk_output_file, chunk_num)
            except subprocess.CalledProcessError as e:
                print(f"Error during FFmpeg conversion: {e}")
            finally:
                pbar.close()

    def download_footage_from_m3u8(self, final_url, total_duration, camera_id, pbar, output_file, chunk_num):
        command = [
            "ffmpeg", "-loglevel", "quiet", "-progress", "-", "-threads", "4", "-i", final_url, "-c", "copy", output_file
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        start_time = time.time()
        while True:
            output = process.stdout.readline().decode()
            if output == '' and process.poll() is not None:
                break
            if output and "out_time=" in output:
                time_str = output.split("out_time=")[-1].split()[0]
                time_parts = time_str.split(':')
                elapsed_seconds = (int(time_parts[0]) * 3600 +
                                   int(time_parts[1]) * 60 +
                                   float(time_parts[2]))
                pbar.n = int(elapsed_seconds)
                pbar.refresh()

        process.wait()
        if process.returncode == 0:
            print(f"\nCamera {camera_id} Chunk {chunk_num}: Footage saved to {output_file}")
        else:
            print(f"\nError during FFmpeg conversion for camera {camera_id} Chunk {chunk_num}: {process.returncode}")

    def download_all_cameras(self, org_id, start_time, end_time, max_concurrent_downloads=3):
        camera_ids = self.get_camera_ids()
        semaphore = threading.Semaphore(max_concurrent_downloads)
        chunk_size = timedelta(seconds=3600)

        threads = []
        position = 0  # Track the position for tqdm bars
        for camera_id in camera_ids.keys():
            chunk_start = start_time
            chunk_num = 0

            while chunk_start < end_time:
                chunk_end = min(chunk_start + chunk_size, end_time)
                thread = threading.Thread(
                    target=self.get_historic_footage_chunk,
                    args=(camera_id, org_id, chunk_start, chunk_end, chunk_num, semaphore, position)
                )
                threads.append(thread)
                thread.start()
                
                chunk_start = chunk_end
                chunk_num += 1
                position += 1  # Increment position for the next progress bar

        for thread in threads:
            thread.join()

        print("All camera downloads complete.")
        self.concatenate_chunks(camera_ids)

    def concatenate_chunks(self, camera_ids):
        video_folder = "video"
        for camera_id in camera_ids.keys():
            if chunk_files := sorted(
                [
                    os.path.join(video_folder, f)
                    for f in os.listdir(video_folder)
                    if f.startswith(camera_id) and f.endswith(".mp4")
                ]
            ):
                output_file = os.path.join(video_folder, f"{camera_id}_complete.mp4")
                concat_file = os.path.join(video_folder, f"{camera_id}_concat.txt")

                with open(concat_file, 'w') as f:
                    for chunk_file in chunk_files:
                        f.write(f"file '{chunk_file}'\n")

                command = [
                    "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", output_file
                ]
                subprocess.run(command, check=True)
                print(f"Camera {camera_id}: All chunks concatenated into {output_file}")
    """
        Posts a Helix event to the Verkada API.

        Args:
            org_id (str): The organization ID.
            camera_id (str): The camera ID.
            attributes (dict): A dictionary of event attributes.
            time_ms (int): The timestamp of the event in milliseconds.
            event_type_uid (str): The event type UID. Default is the Helix event UID.
        
        Returns:
            response: The API response object.
    """
    def post_helix_event(self, camera_id, attributes, time_ms, event_type_uid, org_id=None):
        if org_id is None:
            org_id=self.ORG_ID
        headers = {
            "content-type": "application/json",
            "x-api-key": self.API_KEY
        }
        data = {
            "attributes": attributes,
            "event_type_uid": event_type_uid,
            "camera_id": camera_id,
            "time_ms": time_ms
        }
        return self.send_request(endpoint=f"{EP_HELIX}?org_id={org_id}", params=data)
        
