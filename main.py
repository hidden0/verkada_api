#!/usr/bin/env python3
import sys
import os
# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import time
from pprint import pprint
from library.base_vapi import BaseVapi


def main():
    # Initialize the Vapi instance
    vapi = BaseVapi()
    
if __name__ == "__main__":
    main()
