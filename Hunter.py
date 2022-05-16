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
             if image_link:
                try:
                    # Set fake user agent as Facebook blocks Python requests default user agent
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'}
                    # Get target image using requests, providing Selenium cookies, and fake user agent
                    response = requests.get(image_link, cookies=cookies, headers=headers, stream=True)
                    with open('potential_target_image.jpg', 'wb') as out_file:
                        # Facebook images are sent content encoded so need to decode them
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, out_file)
                    del response
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        # print profilelink + " + " + cdnpicture + " + " + image_link
                        # print result
                        # print ""
                        # check here to do early break if using fast mode, otherwise if accurate set highest distance in array then do a check for highest afterwards
                        if args.mode == "fast":
                            if result < threshold:
                                person.facebook = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.facebookimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                person.facebookcdnimage = encoding.smart_str(cdnpicture, encoding='ascii',
                                                                             errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tFacebook: " + person.facebook)
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            # code for accurate mode here, check if result is higher than current distance (best match in photo with multiple people) and store highest for later comparison
                            if result < threshold:
                                # print "Adding to updated list"
                                # print distance
                                # print "Match over threshold: \n" + profilelink + "\n" + result
                                updatedlist.append([profilelink, image_link, result, cdnpicture])
                except Exception as e:
                    print(e)
                    # print(e)
                    # print "Error getting image link, retrying login and getting fresh cookies"
                    # FacebookfinderObject.doLogin(facebook_username,facebook_password)
                    # cookies = FacebookfinderObject.getCookies()
                    continue
        # For accurate mode pull out largest distance and if it's bigger than the threshold then it's the most accurate result
