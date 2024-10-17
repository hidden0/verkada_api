#!/usr/bin/env python3
import sys
import os
import argparse
from pprint import pprint

# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library.lpr_vapi import LprVapi

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Manage License Plates of Interest (LPOI) in the Verkada platform.")
    parser.add_argument('-a', '--add', metavar='plate', help='Add a license plate to the list of interest.')
    parser.add_argument('-u', '--update', metavar='plate', help='Update a license plate in the list of interest.')
    parser.add_argument('-d', '--delete', metavar='plate', help='Delete a license plate from the list of interest.')
    parser.add_argument('-desc', '--description', metavar='desc', help='Description for the license plate (optional).')
    
    args = parser.parse_args()
    # Initialize the Vapi instance
    vlpr = LprVapi()
    description = args.description or "No description provided"
    if args.add:
        result = vlpr.create_license_plate_of_interest(args.add, description)
        if(result.status_code==200):
            print(f"License plate {args.add} added with description: {description}")
        else:
            print(f"Failed to create plate {args.add} with description: {description}")

    elif args.update:
        result = vlpr.update_license_plate_of_interest(args.update, description=description)
        if(result.status_code==200):
            print(f"License plate {args.update} updated with description: {description}")
        else:
            print(f"Failed to update plate {args.add} with description: {description}")
        
    elif args.delete:
        result = vlpr.delete_license_plate_of_interest(args.delete)
        print(result['status'])
        

    else:
        print("Please specify an action: --add (-a), --update (-u),  or --delete (-d)")
        parser.print_help()

if __name__ == "__main__":
    main()
