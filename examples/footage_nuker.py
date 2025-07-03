#!/usr/bin/env python3
import sys
import os
# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library.base_vapi import BaseVapi

def main():
    # Initialize the Vapi instance
    vapi = BaseVapi()
    print(vapi.api_default_cred_file)
    print(vapi._key_test)
if __name__ == "__main__":
    main()
