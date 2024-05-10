#!/usr/bin/env python3
#imports
from lib.vapi import vapi
from pprint import pprint

def main():
        print("Verkada API Framework")

        myAPI = vapi()
        response = myAPI.sendRequest(product="core", endpoint="user", params=)
        pprint(response.text)

if __name__ == "__main__":
	main()