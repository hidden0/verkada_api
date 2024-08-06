import traceback

# ANSI escape codes for colors
class colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def colorize(color, text):
        return color + text + colors.RESET

    @staticmethod
    def print_error(e):
        error_prefix = colors.colorize(colors.YELLOW, "Error Message: ")
        error_message = colors.colorize(colors.CYAN, str(e.message))
        print(error_prefix + error_message)

        error_prefix = colors.colorize(colors.YELLOW, "Endpoint: ")
        error_message = colors.colorize(colors.CYAN, str(e.endpoint))
        print(error_prefix + error_message)

        error_prefix = colors.colorize(colors.YELLOW, "API Key: ")
        error_message = colors.colorize(colors.CYAN, str(e.api_key))
        print(error_prefix + error_message)

        error_prefix = colors.colorize(colors.YELLOW, "Traceback: ")
        error_message = colors.colorize(colors.RED, ''.join(e.traceback_info))
        print(error_prefix + error_message)

class BaseAPIException(Exception):
    """Base exception class for API errors."""
    def __init__(self, message, code=None, endpoint=None, api_key=None):
        self.message = message
        self.code = code
        self.endpoint = endpoint
        self.api_key = api_key
        self.traceback_info = traceback.format_stack()
        super().__init__(self.format_message())

    def format_message(self):
        base_message = f"{self.message}\n"
        if self.endpoint:
            base_message += f"Endpoint: {self.endpoint}\n"
        if self.api_key:
            base_message += f"API Key: {self.api_key}\n"
        base_message += f"\nTraceback:\n{''.join(self.traceback_info)}"
        return base_message

    def __str__(self):
        return self.format_message()

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
