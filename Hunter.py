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

from Mod import douban
from Mod import facebook
from Mod import instagram
from Mod import linkedin
from Mod import pinterest
from Mod import twitter
from Mod import vkontakte
from Mod import weibo

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

class PotentialPerson(object):
    full_name = ""
    profile_link = ""
    image_link = ""

    def __init__(self, full_name, profile_link, image_link):
        self.full_name = full_name
        self.profile_link = profile_link
        self.image_link = image_link

    def fill_facebook(peoplelist):
    FacebookfinderObject = facebookfinder.Facebookfinder(showbrowser)
    FacebookfinderObject.doLogin(facebook_username, facebook_password)
    if args.waitafterlogin:
        input("Press Enter to continue after verifying you are logged in...")

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True or args.debug == True:
            print("Facebook Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rFacebook Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        # Testcode to mimic a session timeout
        # if count == 3:
        #    print "triggered delete"
        #    FacebookfinderObject.testdeletecookies()
        #print(person.person_imagelink)
        #print(person.person_image)
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = FacebookfinderObject.getFacebookProfiles(person.first_name, person.last_name,
                                                                       facebook_username, facebook_password)
                if args.debug == True:
                    print(profilelist)
            except:
                continue
        else:
            continue

        early_break = False
        updatedlist = []
        # for profilelink,distance in profilelist:
        for profilelink, profilepic, distance, cdnpicture in profilelist:
            try:
                os.remove("potential_target_image.jpg")
            except:
                pass
            if early_break:
                break
            # image_link = FacebookfinderObject.getProfilePicture(profilelink)
            image_link = profilepic
            # print profilelink
            # print image_link
            # print "----"
            cookies = FacebookfinderObject.getCookies()

