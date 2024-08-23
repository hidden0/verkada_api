#!/usr/bin/env python3
from library.lpr_vapi import LprVapi
from pprint import pprint
def main():
    # Testing new code structure
    lpr = LprVapi()

    #print(lpr.create_license_plate_of_interest("mytest2", 1234568))
    #print(lpr.update_license_plate_of_interest("1234568", "moot"))
    print(lpr.delete_license_plate_of_interest("1234568"))

if __name__ == "__main__":
    main()