from __future__ import print_function

import argparse
import csv
import http.cookiejar
import json
import math
import os
import shutil
import sys
import traceback
import urllib
from datetime import datetime
from shutil import copyfile

import face_recognition
import requests
from bs4 import BeautifulSoup
from django.utils import encoding
