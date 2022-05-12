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

from Mod import doubanfinder
from Mod import facebookfinder
from Mod import instagramfinder
from Mod import linkedinfinder
from Mod import pinterestfinder
from Mod import twitterfinder
from Mod import vkontaktefinder
from Mod import weibofinder

assert sys.version_info >= (3,), "Only Python 3 is currently supported."

global linkedin_username
global linkedin_password
linkedin_username = ""
linkedin_password = ""
global facebook_username
global facebook_password
facebook_username = ""
facebook_password = ""
global twitter_username
global twitter_password
twitter_username = ""
twitter_password = ""
global instagram_username
global instagram_password
instagram_username = ""
instagram_password = ""
global google_username
global google_password
google_username = ""
google_password = ""
global vk_username
global vk_password
vk_username = ""  # Can be mobile or email
vk_password = ""
global weibo_username
global weibo_password
weibo_username = ""  # Can be mobile
weibo_password = ""
global douban_username
global douban_password
douban_username = ""
douban_password = ""
global pinterest_username
global pinterest_password
pinterest_username = ""
pinterest_password = ""

global showbrowser

startTime = datetime.now()

class Person(object):
    first_name = ""
    last_name = ""
    full_name = ""
    person_image = ""
    person_imagelink = ""
    linkedin = ""
    linkedinimage = ""
    facebook = ""
    facebookimage = ""  # higher quality but needs authentication to access
    facebookcdnimage = ""  # lower quality but no authentication, used for HTML output
    twitter = ""
    twitterimage = ""
    instagram = ""
    instagramimage = ""
    vk = ""
    vkimage = ""
    weibo = ""
    weiboimage = ""
    douban = ""
    doubanimage = ""
    pinterest = ""
    pinterestimage = ""

    def __init__(self, first_name, last_name, full_name, person_image):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = full_name
        self.person_image = person_image

