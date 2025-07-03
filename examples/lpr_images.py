#!/usr/bin/env python3
import sys
import os
import argparse
import requests
from datetime import datetime
# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library.lpr_vapi import LprVapi

def download_image(url, output_folder, filename):
    # Make sure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(output_folder, filename)
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename} from {url}")

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Download license plate images from the Verkada platform within a time frame.")
    parser.add_argument('-start', '--start_date', required=True, help='Start date in MM/DD/YYYY format.')
    parser.add_argument('-end', '--end_date', required=True, help='End date in MM/DD/YYYY format.')
    parser.add_argument('-output', '--output_folder', required=True, help='Folder to download images to.')
    parser.add_argument('-camera', '--camera_id', required=True, help='ID of the camera to query images from.')
    parser.add_argument('-size', '--page_size', type=int, default=200, help='Number of results per page (max 200).')

    args = parser.parse_args()

    # Parse dates
    start_timestamp = int(datetime.strptime(args.start_date, '%m/%d/%Y').timestamp())
    end_timestamp = int(datetime.strptime(args.end_date, '%m/%d/%Y').timestamp())

    # Initialize the Vapi instance
    vlpr = LprVapi()
    page_token = None  # Initialize page_token to None for the first request
    total_downloads = 0

    # Paginated requests loop
    while True:
        # Fetch a page of results
        response = vlpr.get_lpr_images(
            camera_id=args.camera_id,
            start_time=start_timestamp,
            end_time=end_timestamp,
            page_size=min(args.page_size, 200),
            page_token=page_token
        )

        if detections := response.get("detections", []):
            # Total images in the current page
            page_total = len(detections)
            print(f"Downloading {page_total} images from current page...")

            for idx, detection in enumerate(detections, start=1):
                image_url = detection.get("image_url")
                license_plate = detection.get("license_plate")
                timestamp = detection.get("timestamp")
                
                if image_url:
                    # Use license plate and timestamp to create a unique filename
                    filename = f"{license_plate}_{timestamp}.jpg"
                    
                    # Print progress for each image download
                    print(f"Downloading image {idx}/{page_total} on this page...")
                    
                    # Download the image
                    download_image(image_url, args.output_folder, filename)
                    total_downloads += 1

            # Check for next page_token in response
            page_token = response.get("page_token")
            if not page_token:
                # No more pages left
                break
        else:
            print("No detections found in the specified time frame.")
            break

    print(f"Download completed. Total images downloaded: {total_downloads}")

if __name__ == "__main__":
    main()
