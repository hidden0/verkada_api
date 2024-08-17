import sys
import os
# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import requests
from unittest.mock import patch, mock_open, MagicMock
from library.vapi import Vapi
from library import utils
import json
from datetime import datetime, timedelta
@pytest.fixture
def vapi_instance():
    return Vapi(run_test=False)

@pytest.mark.parametrize("env_var, cred_file, key_type, expected_key, expected_method", [
    ("VERKADA_API_KEY", "api.cred", "API", "test_api_key", "API from ENV"),
    ("VERKADA_STREAMING_API_KEY", "stream_api.cred", "Streaming API", "test_streaming_key", "Streaming API from ENV"),
    ("VERKADA_API_KEY", "api.cred", "API", None, "API from INPUT"),
], ids=["env_var_api_key", "env_var_streaming_key", "input_api_key"])
def test_load_api_key(env_var, cred_file, key_type, expected_key, expected_method, vapi_instance):
    # Arrange
    with patch("os.getenv", return_value=expected_key):
        with patch("builtins.input", return_value=expected_key):
            with patch("builtins.open", mock_open(read_data=expected_key)):

                # Act
                api_key = vapi_instance.load_api_key(env_var, cred_file, key_type)

                # Assert
                assert api_key == expected_key
                assert vapi_instance.API_KEY_METHOD == expected_method

@pytest.mark.parametrize("api_key, endpoint, params, status_code, expected_response", [
    ("test_api_key", "test_endpoint", None, 200, {"data": "test"}),
    ("test_api_key", "test_endpoint", None, 404, None),
], ids=["valid_request", "not_found"])
def test_send_request(api_key, endpoint, params, status_code, expected_response, vapi_instance):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = expected_response
    with patch("requests.get", return_value=mock_response):

        # Act
        response = vapi_instance.send_request(api_key, endpoint, params)

        # Assert
        if status_code == 200:
            assert response.json() == expected_response
        else:
            assert response is None

@pytest.mark.parametrize("status_code, exception", [
    (400, utils.ClientErrorBadRequest),
    (401, utils.ClientErrorUnauthorized),
    (403, utils.ClientErrorForbidden),
    (404, utils.ClientErrorNotFound),
    (429, utils.ClientErrorTooManyRequests),
    (500, utils.ServerErrorInternal),
], ids=["bad_request", "unauthorized", "forbidden", "not_found", "too_many_requests", "internal_server_error"])
def test_handle_http_errors(status_code, exception, vapi_instance):
    # Act & Assert
    with pytest.raises(exception):
        vapi_instance.handle_http_errors(status_code, "test_endpoint", "test_key")

@pytest.mark.parametrize("config_file, file_exists, expected_exception", [
    ("config.ini", True, None),
    ("missing_config.ini", False, utils.FailedConfigLoad),
], ids=["valid_config", "missing_config"])
def test_load_config(config_file, file_exists, expected_exception, vapi_instance):
    # Arrange
    with patch("os.path.exists", return_value=file_exists):
        with patch("configparser.ConfigParser.read", return_value=None):
            if file_exists:
                with patch("configparser.ConfigParser.__getitem__", return_value={
                    'api_url': 'http://test.api',
                    'API_DEFAULT_CREDENTIALS_FILE': 'api.cred',
                    'API_DEFAULT_STREAMING_CREDENTIALS_FILE': 'stream_api.cred',
                    'API_ENVIRONMENT_VARIABLE': 'VERKADA_API_KEY',
                    'API_STREAMING_ENVIRONMENT_VARIABLE': 'VERKADA_STREAMING_API_KEY',
                    'ORG_ID': 'test_org_id'
                }):

                    # Act
                    vapi_instance.load_config(config_file)

                    # Assert
                    assert vapi_instance.API_URL == 'http://test.api'
                    assert vapi_instance.API_DEFAULT_CRED_FILE == 'api.cred'
                    assert vapi_instance.API_DEFAULT_STREAMING_CRED_FILE == 'stream_api.cred'
                    assert vapi_instance.API_ENV_VAR_NAME == 'VERKADA_API_KEY'
                    assert vapi_instance.API_STREAMING_ENVIRONMENT_VAR_NAME == 'VERKADA_STREAMING_API_KEY'
                    assert vapi_instance.ORG_ID == 'test_org_id'
            else:
                # Act & Assert
                with pytest.raises(expected_exception):
                    vapi_instance.load_config(config_file)

@pytest.mark.parametrize("key, expected_result", [
    ("vkd_api_valid_key_12345678901234567890", 0),
    ("invalid_key_length", None),
    ("invalid_format_key_12345678901234567890", None),
], ids=["valid_key", "invalid_length", "invalid_format"])
def test_key_test(key, expected_result, vapi_instance):
    # Arrange
    with patch.object(vapi_instance, 'send_request', return_value=MagicMock(status_code=200)):
        with patch("library.utils.InvalidAPIKeyLength", side_effect=Exception("Invalid length")):
            with patch("library.utils.InvalidAPIKeyFormat", side_effect=Exception("Invalid format")):

                # Act
                result = vapi_instance.key_test(key)

                # Assert
                if expected_result is not None:
                    assert result == expected_result
                else:
                    assert result is None

@pytest.mark.parametrize("response_status, expected_result", [
    (200, ["site1", "site2"]),
    (404, []),
], ids=["valid_response", "not_found"])
def test_get_alarm_site_ids(response_status, expected_result, vapi_instance):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = response_status
    mock_response.json.return_value = {"sites": [{"site_id": "site1"}, {"site_id": "site2"}]}
    with patch.object(vapi_instance, 'send_request', return_value=mock_response):

        # Act
        result = vapi_instance.get_alarm_site_ids()

        # Assert
        assert result == expected_result

@pytest.mark.parametrize("response_status, expected_result", [
    (200, {"device1": {"product": "alarms"}}),
    (404, {}),
], ids=["valid_response", "not_found"])
def test_get_alarm_ids(response_status, expected_result, vapi_instance):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = response_status
    mock_response.json.return_value = {"devices": [{"device_id": "device1"}]}
    with patch.object(vapi_instance, 'get_alarm_site_ids', return_value=["site1"]):
        with patch.object(vapi_instance, 'send_request', return_value=mock_response):

            # Act
            result = vapi_instance.get_alarm_ids()

            # Assert
            assert result == expected_result

@pytest.mark.parametrize("response_status, expected_result", [
    (200, {"camera1": {"product": "camera"}}),
    (404, {}),
], ids=["valid_response", "not_found"])
def test_get_camera_ids(response_status, expected_result, vapi_instance):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = response_status
    mock_response.json.return_value = {"cameras": [{"camera_id": "camera1"}]}
    with patch.object(vapi_instance, 'send_request', return_value=mock_response):

        # Act
        result = vapi_instance.get_camera_ids()

        # Assert
        assert result == expected_result

@pytest.mark.parametrize("product, expected_result", [
    ("all", {"device1": {"product": "alarms"}, "camera1": {"product": "camera"}}),
    ("alarms", {"device1": {"product": "alarms"}}),
    ("cameras", {"camera1": {"product": "camera"}}),
    ("invalid", {}),
], ids=["all_products", "alarms_only", "cameras_only", "invalid_product"])
def test_get_device_ids(product, expected_result, vapi_instance):
    # Arrange
    with patch.object(vapi_instance, 'get_alarm_ids', return_value={"device1": {"product": "alarms"}}):
        with patch.object(vapi_instance, 'get_camera_ids', return_value={"camera1": {"product": "camera"}}):

            # Act
            result = vapi_instance.get_device_ids(product)

            # Assert
            assert result == expected_result

@pytest.mark.parametrize("device_dict, product_type, expected_result", [
    ({"device1": {"product": "alarms"}, "camera1": {"product": "camera"}}, "alarms", {"device1": {"product": "alarms"}}),
    ({"device1": {"product": "alarms"}, "camera1": {"product": "camera"}}, "camera", {"camera1": {"product": "camera"}}),
], ids=["filter_alarms", "filter_cameras"])
def test_filter_by_product_type(device_dict, product_type, expected_result, vapi_instance):
    # Act
    result = vapi_instance.filter_by_product_type(device_dict, product_type)

    # Assert
    assert result == expected_result

@pytest.mark.parametrize("token_exists, token_valid, expected_token", [
    (True, True, "existing_token"),
    (True, False, "new_token"),
    (False, False, "new_token"),
], ids=["existing_valid_token", "existing_invalid_token", "no_token"])
def test_get_stream_token(token_exists, token_valid, expected_token, vapi_instance):
    # Arrange
    with patch("os.path.exists", return_value=token_exists):
        with patch("builtins.open", mock_open(read_data=json.dumps({"token": "existing_token", "timestamp": (datetime.now() - timedelta(seconds=1800)).isoformat()}))):
            with patch.object(vapi_instance, 'send_streaming_request', return_value=MagicMock(status_code=200, json=lambda: {"jwt": "new_token"})):

                # Act
                token = vapi_instance.get_stream_token()

                # Assert
                assert token == expected_token
