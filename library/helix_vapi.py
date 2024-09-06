from library.base_vapi import BaseVapi
import library.utils as utils
import pprint as pprint
class HelixVapi(BaseVapi):
    """
    HelixVapi provides a set of methods for interacting with the Helix API, allowing management of events, event types, 
    and searches within the Helix system.

    Inherits from:
        BaseVapi: A base class providing common API functionality such as sending requests and handling responses.

    Methods:
        delete_helix_event(camera_id, event_time_ms, event_uid):
            Deletes a specific Helix event based on camera ID, event time, and event type UID.

        delete_helix_event_type(event_uid):
            Deletes a specific Helix event type based on its unique identifier.

        get_helix_event(camera_id, event_time_ms, event_uid):
            Retrieves the details of a specific Helix event.

        get_helix_event_types(event_uid=None, event_name=None):
            Retrieves event types based on event UID and/or event name.

        update_helix_event(camera_id, event_time_ms, event_uid, payload):
            Updates the details of a specific Helix event.

        update_helix_event_type(event_type_uid, event_schema):
            Updates the schema of a specific Helix event type.

        create_helix_event_type(event_schema):
            Creates a new Helix event type.

        create_helix_event(camera_id, attributes, time_ms, event_type_uid, org_id=None):
            Creates a new Helix event.

        search_helix_events(attribute_filters=None, camera_ids=None, event_start_time_ms=None, event_end_time_ms=None, event_uid=None, flagged=None, keywords=None):
            Searches for Helix events based on provided filters.
    """
    def __init__(self, run_test=False):
        super().__init__(run_test)
    
    def delete_helix_event(self, camera_id, event_time_ms, event_uid):
        """
        Deletes a specific Helix event.

        Args:
            camera_id (str): The unique identifier of the camera associated with the event.
            event_time_ms (int): The timestamp of the event in milliseconds since the epoch.
            event_uid (str): The unique identifier of the event type.

        Returns:
            dict: The API response confirming the deletion of the event.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        params = {
            "camera_id": camera_id,
            "time_ms": event_time_ms,
            "event_type_uid": event_uid
        }
        return self.send_request(self.ENDPOINTS['helix_event'], params=params, method="DELETE")
    
    def delete_helix_event_type(self, event_uid):
        """
        Deletes a specific Helix event type.

        Args:
            event_uid (str): The unique identifier of the event type to be deleted.

        Returns:
            dict: The API response confirming the deletion of the event type.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        params = {
            "event_type_uid": event_uid
        }
        return self.send_request(self.ENDPOINTS['helix_event'], params=params, method="DELETE")

    def get_helix_event(self, camera_id, event_time_ms, event_uid):
        """
        Retrieves a specific Helix event.

        Args:
            camera_id (str): The unique identifier of the camera associated with the event.
            event_time_ms (int): The timestamp of the event in milliseconds since the epoch.
            event_uid (str): The unique identifier of the event type.

        Returns:
            dict: The API response containing the details of the event.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        params = {
            "camera_id": camera_id,
            "time_ms": event_time_ms,
            "event_type_uid": event_uid
        }
        return self.send_request(self.ENDPOINTS['helix_event'], params=params, method="GET")
    
    def get_helix_event_types(self, event_uid=None, event_name=None):
        """
        Retrieves event types based on event UID and/or event name.

        Args:
            event_uid (str, optional): The unique identifier for the event type.
            event_name (str, optional): The name of the event type.

        Returns:
            dict: The API response containing event types.
        """
        # Initialize an empty params dictionary
        params = {}

        # Add event_uid to params if it is provided
        if event_uid is not None:
            params["event_type_uid"] = event_uid

        # Add event_name to params if it is provided
        if event_name is not None:
            params["event_name"] = event_name

        return self.send_request(self.ENDPOINTS['helix_event_type'], params=params, method="GET")

    def update_helix_event(self, camera_id, event_time_ms, event_uid, payload):
        """
        Updates a specific Helix event's details.

        This method sends a PATCH request to update the details of a Helix event identified by the camera ID, event time, and event type UID. The updated information is provided in the payload.

        Args:
            camera_id (str): The unique identifier of the camera associated with the event.
            event_time_ms (int): The timestamp of the event in milliseconds since the epoch.
            event_uid (str): The unique identifier of the event type.
            payload (dict): A dictionary containing the updated event data. This should include the new or modified attributes of the event.

        Returns:
            dict: The API response containing the details of the updated event, or an error message if the update fails.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        params = {
            "camera_id": camera_id,
            "time_ms": event_time_ms,
            "event_type_uid": event_uid
        }
        return self.send_request(self.ENDPOINTS['helix_event'], json=payload, params=params, method="PATCH")

    def update_helix_event_type(self, event_type_uid, event_schema):
        """
        Updates the schema of a specific Helix event type.

        This method sends a PATCH request to update the schema of the Helix event type identified by the provided event_type_uid.
        
        Args:
            event_type_uid (str): The unique identifier of the event type to be updated.
            event_schema (dict): The schema data that defines the updated properties of the event type. This should be a dictionary containing the new or modified attributes of the event type.

        Returns:
            dict: The API response containing the details of the updated event type, or an error message if the update fails.
        
        Raises:
            HTTPError: If the response status code indicates an error.
        """
        params = {"event_type_uid": event_type_uid}
        return self.send_request(self.ENDPOINTS['helix_event_type'], json=event_schema, params=params, method="PATCH")
    
    def create_helix_event_type(self, event_schema):
        """
        Creates a new Helix event type.

        Args:
            event_schema (dict): A dictionary containing the schema data that defines the properties of the new event type.

        Returns:
            dict: The API response containing the details of the newly created event type.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        return self.send_request(self.ENDPOINTS['helix_event_type'], json=event_schema, method="POST")
    
    def create_helix_event(self, camera_id, attributes, time_ms, event_type_uid, org_id=None):
        """
        Creates a new Helix event.

        Args:
            camera_id (str): The unique identifier of the camera associated with the event.
            attributes (dict): A dictionary containing the attributes of the event.
            time_ms (int): The timestamp of the event in milliseconds since the epoch.
            event_type_uid (str): The unique identifier of the event type.
            org_id (str, optional): The organization ID. If not provided, the default org_id of the instance is used.

        Returns:
            dict: The API response containing the details of the newly created event.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        if org_id is None:
            org_id=self.org_id
        headers = {
            "content-type": "application/json",
            "x-api-key": self.api_key
        }
        data = {
            "attributes": attributes,
            "event_type_uid": event_type_uid,
            "camera_id": camera_id,
            "time_ms": time_ms, 
        }
        return self.send_request(endpoint=self.ENDPOINTS['helix_event'], json=data, params=org_id, method="POST")
    
    def search_helix_events(self, attribute_filters=None, camera_ids=None, event_start_time_ms=None, event_end_time_ms=None, event_uid=None, flagged=None, keywords=None):
        """
        Searches for Helix events based on provided filters.
        
        All parameters are optional and will only be included in the query if provided.
        
        Args:
            attribute_filters (dict): Filters for attributes.
            camera_ids (list): List of camera IDs to search.
            event_start_time_ms (int): Start time of the event in milliseconds.
            event_end_time_ms (int): End time of the event in milliseconds.
            event_uid (str): Unique ID for the event.
            flagged (bool): Whether the event is flagged.
            keywords (str): Keywords to search for in events.
        
        Returns:
            dict: The search results from the API.
        """
         # Construct the query parameters dynamically
        
        payload = {}
        
        if attribute_filters is not None:
            payload['attribute_filters'] = attribute_filters
        if camera_ids is not None:
            payload['camera_ids'] = ','.join(camera_ids)  # Convert list to comma-separated string
        if event_start_time_ms is not None:
            payload['event_start_time_ms'] = event_start_time_ms
        if event_end_time_ms is not None:
            payload['event_end_time_ms'] = event_end_time_ms
        if event_uid is not None:
            payload['event_uid'] = event_uid
        if flagged is not None:
            payload['flagged'] = flagged
        if keywords is not None:
            payload['keywords'] = keywords
        
        return self.send_request(self.ENDPOINTS['helix_event_search'], data=None, json=payload, params=None, method="POST")
