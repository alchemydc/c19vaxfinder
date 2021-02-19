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
from datetime import date

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
DISCORD_WEBHOOK         = os.getenv('DISCORD_WEBHOOK')


# constants
LATLONG_FILE          = './static_data/latlong_data.json'
WALGREENS_API         = 'https://www.walgreens.com/hcschedulersvc/svc/v1/immunizationLocations/availability'
WALGREENS_URI         = 'https://www.walgreens.com/findcare/vaccination/covid-19/location-screening'
DISCORD_AVATAR        = 'https://img.webmd.com/dtmcms/live/webmd/consumer_assets/site_images/article_thumbnails/other/1800x1200_virus_3d_render_red_03_other.jpg?resize=*:350px'
DISCORD_ICON          = 'http://s3.amazonaws.com/pix.iemoji.com/images/emoji/apple/ios-12/256/syringe.png'
DISCORD_NICK          = 'C19'

http_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

# fcns
def readFile(filename):
    with open(filename, 'r') as myfile:
        data = myfile.read()
    obj = json.loads(data)
    return(obj)

def checkAvailability(locations):
    
    for location in locations:
        
        #print(location['zip'])
        #print(location['latitude'])
        #print(location['longitude'])
        #print(location['name'])
        
        print("checking availability in %s" % location['name'])
        payload = {
            "serviceId" :"99",
            "position"  :
                {
                    "latitude"  :   location['latitude'],
                    "longitude" :   location['longitude']
                },
            "appointmentAvailability":
                {
                    #"startDateTime":"2021-02-19"                              # FIXME: need to use current date in this format date.today().strftime("%Y-%m-%d")
                    "startDateTime": date.today().strftime("%Y-%m-%d")         
                },
            "radius":25
        }
    
        response = http.post(WALGREENS_API, headers = http_headers, json = payload)
        data = response.json()
        isAvailable = data['appointmentsAvailable']
        if isAvailable:
            print("Good news, there is an appointment available at %s, ZIP %s" % (location['name'], location['zip']) )
            discordEmbed(location, DISCORD_WEBHOOK)
        else:
            print("Sorry, no appointment available at %s" % location['name'])
        
def discordEmbed(data, discord_uri):
    print("Sending alert data to discord at %s" % (discord_uri))
    http_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    description = "C19 vaccination appointment available for %s" % data['name']
    
    payload = {
        "username": DISCORD_NICK,
        "avatar_url": DISCORD_AVATAR,

        "embeds": [
            {
                "author": 
                    {
                        "name"      : "C19 Vaccine",
                        "url"       : WALGREENS_URI,
                        "icon_url"  : DISCORD_ICON
                    },            

                "title"      : "Time to get your shot!",
                "url"        : WALGREENS_URI,
                "description": description,
                "color"      :  15258703,
                "thumbnail"  :
                    {
                        "url": WALGREENS_URI
                    },
                }
            ]
        }
    response = http.post(discord_uri, headers=http_headers, json=payload)

def main():
    locations = readFile(LATLONG_FILE)
    checkAvailability(locations)
        

if __name__ == "__main__":
    main()