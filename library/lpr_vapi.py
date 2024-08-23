from library.camera_vapi import CameraVapi

class LprVapi(CameraVapi):
    def __init__(self, run_test=False):
        super().__init__(run_test)

    def get_lpr_images(self, camera_id, start_time=None, end_time=None, license_plate=None):
        """
        Retrieves images captured by cameras that have recognized license plates.

        HTTP Method: GET

        Args:
            camera_id (str): The ID of the camera.
            start_time (int, optional): Start timestamp to filter images.
            end_time (int, optional): End timestamp to filter images.
            license_plate (str, optional): License plate to filter images.

        Returns:
            dict: The API response containing LPR images.
        """
        pass

    def delete_license_plate_of_interest(self, license_plate_id):
        """
        Deletes a specific License Plate of Interest (LPOI) from the system.

        HTTP Method: DELETE

        Args:
            license_plate_id (str): The unique identifier of the license plate of interest to be deleted.

        Returns:
            dict: The API response confirming the deletion of the license plate of interest.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        endpoint = f"{self.ENDPOINTS['license_plate_of_interest']}"
        response = self.send_request(endpoint, params={"license_plate": license_plate_id}, method="DELETE")

        # Handle errors and return response
        if response.status_code != 200:  # 204 No Content is typically the response for successful deletions
            response.raise_for_status()

        return {"status": "Deleted successfully"}  # or return response content if the API provides some


    def get_license_plate_of_interest(self, license_plate_id):
        """
        Retrieves details about a specific license plate of interest.

        HTTP Method: GET

        Args:
            license_plate_id (str): The unique identifier of the license plate of interest.

        Returns:
            dict: The API response containing the license plate details.
        """
        pass

    def update_license_plate_of_interest(self, license_plate_id, description):
        """
        Updates details of an existing License Plate of Interest (LPOI).

        HTTP Method: PATCH

        Args:
            license_plate_id (str): The unique identifier of the license plate of interest.
            data (str): A string containing the updated data for the license plate.

        Returns:
            dict: The API response containing the updated details of the license plate of interest.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        endpoint = f"{self.ENDPOINTS['license_plate_of_interest']}"
        payload = {"description": description}

        # Send the PATCH request with JSON body
        response = self.send_request(endpoint, data=None, json=payload, params={"license_plate": license_plate_id}, method="PATCH")

        # Handle errors and return response
        if response.status_code != 200:
            response.raise_for_status()

        return response.json()


    def create_license_plate_of_interest(self, license_plate_id, description):
        """
        Adds a new License Plate of Interest (LPOI) to the system.

        HTTP Method: POST

        Args:
            description: A dictionary containing the "description" of the new license plate, such as the plate number, associated vehicle details, and reasons for adding to the list.
            plate: The license plate to update
        Example:

        Returns:
            dict: The API response containing the details of the created license plate of interest.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        endpoint = self.ENDPOINTS['license_plate_of_interest']
        response = self.send_request(endpoint, json={"description": description, "license_plate": license_plate_id}, method="POST")

        # Handle errors and return response
        if response.status_code != 200:
            response.raise_for_status()

        return response.json()

        

    def get_lpr_timestamps(self, camera_id, license_plate=None, start_time=None, end_time=None):
        """
        Retrieves timestamps associated with license plate recognition events.

        HTTP Method: GET

        Args:
            camera_id (str): The ID of the camera.
            license_plate (str, optional): License plate to filter timestamps.
            start_time (int, optional): Start timestamp to filter events.
            end_time (int, optional): End timestamp to filter events.

        Returns:
            dict: The API response containing LPR timestamps.
        """
        pass
