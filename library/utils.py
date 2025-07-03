# utils.py
import traceback
import logging

# ANSI escape codes for colors
class colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"

    @staticmethod
    def colorize(color, text):
        return color + text + colors.RESET

    @staticmethod
    def print_error(e):
        error_details = [
            ("Error Message", e.message),
            ("Endpoint", e.endpoint),
            ("API Key", e.api_key),
            ("Traceback", ''.join(e.traceback_info))
        ]

        for label, detail in error_details:
            if detail:
                print(
                    f"{colors.colorize(colors.YELLOW, f'{label}:')} {colors.colorize(colors.CYAN, str(detail))}"
                )

        exit(e.code)

# General Error Handler Class
class ErrorHandler:
    def __init__(self, log_file="errors.log"):
        logging.basicConfig(filename=log_file, level=logging.ERROR,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def handle(self, error, custom_message="An error occurred"):
        # Log the error details
        logging.error(f"{custom_message}: {str(error)}")
        logging.error(f"Traceback: {traceback.format_exc()}")

        # Print the error details to the console for immediate feedback
        print(f"{colors.colorize(colors.RED, custom_message)}")
        print(f"{colors.colorize(colors.CYAN, str(error))}")
        print(f"Traceback: {traceback.format_exc()}")

# Initialize a global instance
error_handler = ErrorHandler()
class BaseAPIException(Exception):
    """Base exception class for API errors."""
    def __init__(self, message, code=None, endpoint=None, api_key=None):
        self.message = message
        self.code = code
        self.endpoint = endpoint
        self.api_key = api_key
        self.traceback_info = traceback.format_stack()
        super().__init__(colors.print_error(self))

class FailedConfigLoad(BaseAPIException):
    """Custom exception class for Verkada API framework."""
    def __init__(self, endpoint=None, api_key=None):
        message = """Unable to load config file. Please be sure that 'config.api' exists and has the following format:
        [DEFAULT]
        API_URL = "https://api.verkada.com"
        API_VERSION = "v1"
        API_DEFAULT_CREDENTIALS_FILE = "api.cred"
        API_ENVIRONMENT_VARIABLE = "VERKADA_API_KEY" """
        super().__init__(message)

class InvalidAPIKeyLength(BaseAPIException):
    """Custom exception class for API key length being too short or too long"""
    def __init__(self, length):
        message = f"API key length must be exactly 40 characters. This key was {str(length)} characters long."
        super().__init__(message, code=10)

class InvalidAPIKeyFormat(BaseAPIException):
    """Custom exception class for invalid API key format"""
    def __init__(self, endpoint=None, api_key=None):
        message = "API keys must start with vkd_api_"
        super().__init__(message, code=11)

class ClientErrorBadRequest(BaseAPIException):
    """Custom exception for 400 Bad Request errors."""
    def __init__(self, endpoint=None, api_key=None):
        message = "Request response code 400 - Bad Request"
        super().__init__(message, code=12, endpoint=endpoint, api_key=api_key)

class ClientErrorUnauthorized(BaseAPIException):
    """Custom exception for 401 unauthorized error"""
    def __init__(self, endpoint=None, api_key=None):
        message = "Request response code 401 - Unauthorized"
        super().__init__(message, code=13, endpoint=endpoint, api_key=api_key)

class ClientErrorForbidden(BaseAPIException):
    """Custom exception for 403 forbidden error"""
    def __init__(self, endpoint=None, api_key=None):
        message = "Request response code 403 - Forbidden"
        super().__init__(message, code=14, endpoint=endpoint, api_key=api_key)

class ClientErrorNotFound(BaseAPIException):
    """Custom exception for 404 not found error"""
    def __init__(self, endpoint=None, api_key=None):
        message = "Request response code 404 - Endpoint not found"
        super().__init__(message, code=15, endpoint=endpoint, api_key=api_key)

class ClientErrorTooManyRequests(BaseAPIException):
    """Custom exception for 429 too many requests error"""
    def __init__(self, endpoint=None, api_key=None):
        message = "Request response code 429 - Too many requests, rate limited"
        super().__init__(message, code=16, endpoint=endpoint, api_key=api_key)

class ServerErrorInternal(BaseAPIException):
    """Custom exception for 500 internal server error"""
    def __init__(self, endpoint=None, api_key=None):
        message = "Request response code 500 - Internal Server Error"
        super().__init__(message, code=17, endpoint=endpoint, api_key=api_key)
