#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# libs
from c19vaxfinder import *

# local constants
LATLONG_FILE          = './static_data/latlong_data_co.json'

def main():
    #read walgreens lat longs from file
    walgreensLocations = readFile(LATLONG_FILE)
    # check lat longs against walgreens API
    checkWalgreensAvailability(walgreensLocations)

if __name__ == "__main__":
    main()
