from library.base_vapi import BaseVapi
import library.utils as utils
import os
import json
import requests
import tqdm # type: ignore
import subprocess
import threading
from datetime import datetime, timedelta, time
class CameraVapi(BaseVapi):
    def __init__(self, run_test=False):
        super().__init__(run_test)

    def get_camera_devices(self):
        """
        Retrieves a dictionary of camera devices from the API.

        This method sends a request to the camera devices endpoint and processes the response to extract camera IDs. If the request is successful, it returns a dictionary mapping camera IDs to their product type. In case of an error, it handles the HTTP error appropriately.

        Returns:
            dict: A dictionary where keys are camera IDs and values are dictionaries containing product information.

        Raises:
            HTTPError: If the response status code indicates an error.
        """
        endpoint = f"{self.ENDPOINTS['camera_devices']}"
        response = self.send_request(endpoint=endpoint)
        if response.status_code == 200:
            return response.json()
    
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
        response = self.send_streaming_request(endpoint=self.ENDPOINTS['camera_footage_token'], params={"expiration": TTL})

        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("jwt")

            # Store the token with the current timestamp
            with open(token_file, 'w') as f:
                json.dump({"token": token, "timestamp": datetime.now().isoformat()}, f)

            return token
        else:
            self.handle_http_errors(response.status_code, self.ENDPOINTS['camera_footage_token'], self.api_key)
            return None

    '''
    This is experimental code below to stream and save footage in real time with the streaming api
    '''
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

        start_time = time()
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