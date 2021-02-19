#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# libs
import requests
from requests_toolbelt.utils import dump
import json
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# create a custom requests object, modifying the global module throws an error
# provides intrinic exception handling for requests without try/except
http = requests.Session()
assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
http.hooks["response"] = [assert_status_hook]

# dump verbose request and response data to stdout
def logging_hook(response, *args, **kwargs):
    data = dump.dump_all(response)
    print(data.decode('utf-8'))

#setup Requests to log request and response to stdout verbosely
http.hooks["response"] = [logging_hook]

# read secrets from env vars
env_path                = Path('.') / '.env'
load_dotenv(dotenv_path = env_path)
GOOG_GEOCODING_APIKEY    = os.getenv('GOOG_GEOCODING_APIKEY')


# constants

GOOG_LOC_API_BASE     = 'https://maps.googleapis.com/maps/api/geocode/json?key=' + GOOG_GEOCODING_APIKEY + '&components=postal_code:'
ZIPCODE_FILE          = './static_data/walgreens_co_ca_md_zips.txt'
LATLONG_FILE          = './static_data/latlong_data.json'

http_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

# fcns
def readFile(filename):
    #print('hello readFile')
    print('opening file %s for reading' % filename)
    try:
        file = open(filename,'r')
        data = file.readlines()
        file.close()
        return(data)
    except Exception:
        print("Error reading zipcode file")
        sys.exit(1)

def writeFile(data, filename):
    print('opening file %s for writing' % filename)
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def getData(zipcodes):
    decoratedZipcodes = []
    
    for zipcode in zipcodes:
        url = GOOG_LOC_API_BASE + zipcode.rstrip()
        print(url)
        response = http.get(url, headers=http_headers)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == "OK": 
                decoratedZipcodes.append({
                    'zip'       : data['results'][0]['address_components'][0]['long_name'],
                    'latitude'  : data['results'][0]['geometry']['location']['lat'],
                    'longitude' : data['results'][0]['geometry']['location']['lng'],
                    'name'      : data['results'][0]['formatted_address']
                })
    return(decoratedZipcodes)

def main():
    print("using GOOG apikey %s" % GOOG_GEOCODING_APIKEY)
    zipcodes = readFile(ZIPCODE_FILE)
    decoratedZipcodes = getData(zipcodes)
    print(decoratedZipcodes)
    writeFile(decoratedZipcodes, LATLONG_FILE)

if __name__ == "__main__":
    main()