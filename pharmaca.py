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
from c19vaxfinder import *


def main():
    checkPharmaca(pharmacaLocations)
        

if __name__ == "__main__":
    main()