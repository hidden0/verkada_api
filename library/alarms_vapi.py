from library.base_vapi import BaseVapi
import library.utils as utils
import sys
class AlarmVapi(BaseVapi):
    def __init__(self, run_test=False):
        super().__init__(run_test)

    def get_alarm_devices(self):
        # Fetch site IDs for alarms and pass as query parameters
        alarm_devices_by_site = {}
        site_ids = self.get_alarm_site_ids()

        if not site_ids:
            print("No site IDs found.")
            return alarm_devices_by_site  # Return an empty dictionary if no site IDs are found

        for site_id in site_ids:
            params = {'site_id': site_id}
            response = self.send_request(endpoint=self.ENDPOINTS['alarm_devices'], params=params)
            
            if response.status_code == 200:
                data = response.json()
                devices = data.get("devices", [])
                
                # Create a dictionary for this site and add all device information
                alarm_devices_by_site[site_id] = {
                    device.get("device_id"): device for device in devices if device.get("device_id")
                }
            else:
                self.handle_http_errors(
                    response.status_code,
                    f"{self.api_url}/{self.ENDPOINTS['alarm_devices']}",
                    self.api_key,
                )
        
        return alarm_devices_by_site
        
    def get_alarm_site_ids(self):
        # TODO [] Get rid of invalid sites 
        invalid_site_id = "e71edc44-f20e-4893-b6d2-c03f41b9e83a"  # The site ID to skip
        try:
            response = self.send_request(endpoint=self.ENDPOINTS['alarm_sites'])
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
                    f"{self.api_url}/{self.ENDPOINTS['alarm_sites']}",
                    self.api_key,
                )

        except utils.BaseAPIException as e:
            utils.colors.print_error(e)
            sys.exit(e.code)