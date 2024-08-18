from library.base_vapi import BaseVapi
import library.utils as utils
import sys
class HelixVapi(BaseVapi):
    def __init__(self, run_test=False):
        super().__init__(run_test)
    
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
        return self.send_request(endpoint=f"{self.ENDPOINTS['helix_event']}?org_id={org_id}", params=data, method="POST")