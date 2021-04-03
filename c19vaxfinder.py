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
from random import randint
from time import sleep

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
#http.hooks["response"] = [logging_hook]

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
PHARMACA_REQ_URI      = 'https://pharmaca.as.me/schedule.php?action=showCalendar&fulldate=1&owner=20105611&template=weekly'
PHARMACA_BASEURI      = 'https://pharmaca.as.me/'
pharmacaLocations = [
        {
            'name'      : "tablemesa",
            'calendar'  : 4602706,
            'calendarID': 4222381,
            'uri'       : PHARMACA_BASEURI + "tablemesa"
        },
        {
            'name'      : "broadway",
            'calendar'  : 4490121,
            'calendarID': 4222367,
            'uri'       : PHARMACA_BASEURI + "broadway"
        },
        {
            'name'      : "menlopark",
            'calendar'  : 5070402,
            'calendarID': 4222528,
            'uri'       : PHARMACA_BASEURI + "menlopark"
        },
        {
            'name'      : "redmond",
            'calendar'  : 4489970,
            'calendarID': 4222468,
            'uri'       : PHARMACA_BASEURI + "redmond"
        },
        {
            'name'      : "westseattle",
            'calendar'  : 4350219,
            'calendarID': 4222468,
            'uri'       : PHARMACA_BASEURI + "westseattle"
        },
        {
            'name'      : "wallingford",
            'calendar'  : 4350225,
            'calendarID': 4222440,
            'uri'       : PHARMACA_BASEURI + "wallingford"
        },
        {
            'name'      : "greenwoodvillage",
            'calendar'  : 5258035,
            'calendarID': 4222456,
            'uri'       : PHARMACA_BASEURI + "redmond"
        }
    ]

MINIMUM_DELAY = 1    # minimum delay is 1s
MAXIMUM_DELAY = 30   # max delay is 30s


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

def checkWalgreensAvailability(locations):
    
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
                    "startDateTime": date.today().strftime("%Y-%m-%d")      #"startDateTime":"2021-02-19"
                },
            "radius":25
        }
    
        response = http.post(WALGREENS_API, headers = http_headers, json = payload)
        if response.status_code == 200:
            data = response.json()
            isAvailable = data['appointmentsAvailable']
            if isAvailable:
                print("Good news, there is an appointment available at Walgreens %s, ZIP %s" % (location['name'], location['zip']) )
                discordEmbed(location, "Walgreens", WALGREENS_URI, DISCORD_WEBHOOK)
            else:
                print("Sorry, no appointment available at %s" % location['name'])
            time_to_sleep = randint(MINIMUM_DELAY, MAXIMUM_DELAY)
            print("Sleeping %i s" % time_to_sleep)
            sleep(time_to_sleep)
        else:
            print("Exception http/%s requesting availability for %s" % (response.status_code, location['name']))
        
def discordEmbed(data, provider, provider_uri, discord_uri):
    print("Sending alert data for provider_uri %s to discord at %s" % (provider_uri, discord_uri))
    http_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    description = "C19 vaccination appointment available at %s for %s" % (provider, data['name'])
    
    payload = {
        "username": DISCORD_NICK,
        "avatar_url": DISCORD_AVATAR,

        "embeds": [
            {
                "author": 
                    {
                        "name"      : "C19 Vaccine",
                        "url"       : provider_uri,
                        "icon_url"  : DISCORD_ICON
                    },            

                "title"      : "Time to get your shot!",
                "url"        : provider_uri,
                "description": description,
                "color"      :  15258703,
                "thumbnail"  :
                    {
                        "url": provider_uri
                    },
                }
            ]
        }
    response = http.post(discord_uri, headers=http_headers, json=payload)

def checkPharmaca(locations):
    #print(location['name'])
    #print(location['calendar'])
    #print(location['calendarID'])
    #print(location['uri'])
    http_headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    for location in locations:
        print("checking Pharmaca availability in %s" % location['name'])
        payload = "type=19573151&calendar=" + str(location['calendar']) + "&skip=true&options%5Bqty%5D=1&options%5BnumDays%5D=5&ignoreAppointment=&appointmentType=&calendarID=" + str(location['calendarID'])
        response = http.post(PHARMACA_REQ_URI, headers = http_headers, data = payload)
        if response.status_code == 200:
            data = response.text
            if data.find("choose-time") >= 0:
                print("woot! found an appointment at Pharmaca on %s" % location['name'])
                discordEmbed(location, "Pharmaca", PHARMACA_BASEURI+location['name'], DISCORD_WEBHOOK)
            else:
                print("no times found. bum deal dude")
        else:
            print("Exception http/%s requesting availability for %s" % (response.status_code, location['name']))

