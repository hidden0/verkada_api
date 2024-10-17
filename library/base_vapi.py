import sys
import os
import configparser
import library.utils as utils
import requests
class BaseVapi:
    def __init__(self, run_test=True):
        self.api_key = None
        self.streaming_api_key = None
        self.api_key_method = None
        self.api_url = None
        self.api_key_valid = False
        self.org_id = None
        self.api_endpoint = None
        self.api_endpoint_params = None
        self.api_env_var_name = None
        self.api_default_cred_file = None
        self.api_default_streaming_cred_file = None
        self.api_streaming_environment_var_name = None
        self.api_version = None

        # Load the configuration
        self._load_config()

        # Load API keys
        self.api_key = self._load_api_key(env_var="VERKADA_API_KEY", cred_file=self.api_default_cred_file, key_type="API")
        self.streaming_api_key = self._load_api_key(env_var="VERKADA_STREAMING_API_KEY", cred_file=self.api_default_streaming_cred_file, key_type="Streaming API")
        # Validate the regular API key if run_test is True
        if run_test and self.api_key:
            self._key_test(self.api_key)
        # Grouping related constants into dictionaries
        self.PRODUCTS = {
            "camera": "cameras",
            "core": "core",
            "access": "access",
            "sensor": "environment",
            "guest": "guest",
            "alarms": "alarms",
            "events": "events",
        }
        #https://api.verkada.com/cameras/v1/analytics/lpr/license_plate_of_interest?license_plate_id=0001
        self.ENDPOINTS = {
            "camera_devices": f"{self.PRODUCTS['camera']}/{self.api_version}/devices",
            "camera_footage_token": f"{self.PRODUCTS['camera']}/{self.api_version}/footage/token",
            "alarm_devices": f"{self.PRODUCTS['alarms']}/{self.api_version}/devices",
            "alarm_sites": f"{self.PRODUCTS['alarms']}/{self.api_version}/sites",
            "helix_event": f"{self.PRODUCTS['camera']}/{self.api_version}/video_tagging/event",
            "helix_event_search": f"{self.PRODUCTS['camera']}/{self.api_version}/video_tagging/event/search",
            "helix_event_type": f"{self.PRODUCTS['camera']}/{self.api_version}/video_tagging/event_type",
            "license_plate_of_interest": f"{self.PRODUCTS['camera']}/{self.api_version}/analytics/lpr/license_plate_of_interest",
        }

    def _load_api_key(self, env_var, cred_file, key_type):
        # Avoid using sys.argv[1] directly to prevent command-line flags from being mistaken as API keys.
        temp_api_key = os.getenv(env_var) or self._load_key_from_file(cred_file)

        if temp_api_key is None:
            temp_api_key = input(f"Please enter your {key_type} key: ")
            self.api_key_method = f"{key_type} from INPUT"
        else:
            self.api_key_method = f"{key_type} from {self.api_key_method or 'ENV/FILE'}"

        return temp_api_key


    def _load_key_from_file(self, cred_file):
        """Attempt to load the API key from a credentials file."""
        try:
            with open(cred_file, "r") as f:
                return f.read().strip()
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return None

    def _load_config(self, config_file="config.ini"):
        try:
            if not os.path.exists(config_file):
                raise utils.FailedConfigLoad()

            # Load the API configuration
            config = configparser.ConfigParser()

            # Load the configuration file
            config.read(config_file)

            # Access the configuration values
            self.api_url = config['DEFAULT']['API_URL']
            self.api_default_cred_file = config['DEFAULT']['API_DEFAULT_CREDENTIALS_FILE']
            self.api_default_streaming_cred_file = config['DEFAULT']['API_DEFAULT_STREAMING_CREDENTIALS_FILE']
            self.api_env_var_name = config['DEFAULT']['API_ENVIRONMENT_VARIABLE']
            self.api_streaming_environment_var_name = config['DEFAULT']['API_STREAMING_ENVIRONMENT_VARIABLE']
            self.org_id = config['DEFAULT']['ORG_ID']
            self.api_version = config['DEFAULT']['API_VERSION']

        except Exception as e:
            print(f"Error: {str(e)}")

    def _key_test(self, key):
        """Stub for testing the API key."""
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
            #print(key)
            response = self.send_request(api_key=key, endpoint="core/v1/audit_log?page_size=100")
            if response.status_code == 200:
                self.API_KEY = key
                return 0
            else:
                self.handle_http_errors(response.status_code, "core/v1/audit_log?page_size=100", self.API_KEY)
            print(f"Key tested successfully: {key}")
        except Exception as e:
            utils.colors.print_error(e.message)
            exit(e.code)
    
    def send_request(self, api_key=None, endpoint=None, data=None, json=None, params=None, method="GET"):
        try:
            headers = {}
            if api_key is None:
                headers = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "x-api-key": self.api_key
                }
            else:
                headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "x-api-key": api_key
                }
            url = f"{self.api_url}/{endpoint}"

            # Dynamically build the request arguments
            request_kwargs = {
                "headers": headers,
            }

            if params:
                request_kwargs["params"] = params
            if json:
                request_kwargs["json"] = json
            if data:
                request_kwargs["data"] = data

            # Send the appropriate HTTP request based on method
            if method.upper() == "POST":
                return requests.post(url, **request_kwargs)
            elif method.upper() == "PATCH":
                return requests.patch(url, **request_kwargs)
            elif method.upper() == "PUT":
                return requests.put(url, **request_kwargs)
            elif method.upper() == "DELETE":
                return requests.delete(url, **request_kwargs)
            elif method.upper() == "GET":
                return requests.get(url, **request_kwargs)
            elif method.upper() == "HEAD":
                return requests.head(url, **request_kwargs)
            elif method.upper() == "OPTIONS":
                return requests.options(url, **request_kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except requests.exceptions.RequestException as e:
            utils.error_handler.handle(e, f"HTTP Request failed for URL: {url}")
            return None
        except Exception as e:
            utils.error_handler.handle(e, "Unexpected error in send_request")
            return None
    
    def send_streaming_request(self, endpoint, params=None):
        headers = {
            "accept": "application/json",
            "x-api-key": self.streaming_api_key
        }
        url = f"{self.api_url}/{endpoint}"
        return requests.get(url, headers=headers, params=params)
     
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