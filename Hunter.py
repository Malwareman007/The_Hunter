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
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance, cdnpicture in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
                    bestcdnpicture = cdnpicture
            if highestdistance < threshold:
                person.facebook = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.facebookimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                person.facebookcdnimage = encoding.smart_str(bestcdnpicture, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tFacebook: " + person.facebook)
    try:
        FacebookfinderObject.kill()
    except:
        print("Error Killing Facebook Selenium instance")
    return peoplelist


def fill_pinterest(peoplelist):
    PinterestfinderObject = pinterestfinder.Pinterestfinder(showbrowser)
    PinterestfinderObject.doLogin(pinterest_username, pinterest_password)
    if args.waitafterlogin:
        input("Press Enter to continue after verifying you are logged in...")

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True or args.debug == True:
            print("Pinterest Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rPinterest Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = PinterestfinderObject.getPinterestProfiles(person.first_name, person.last_name)
                if args.debug == True:
                    print(profilelist)
            except:
                continue
        else:
            continue

        early_break = False
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            try:
                os.remove("potential_target_image.jpg")
            except:
                pass
            if early_break:
                break
            image_link = profilepic
            if image_link:
                try:
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if result < threshold:
                                person.pinterest = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.pinterestimage = encoding.smart_str(image_link, encoding='ascii',
                                                                           errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tPinterest: " + person.pinterest)
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            if result < threshold:
                                updatedlist.append([profilelink, image_link, result])
                except:
                    continue
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.pinterest = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.pinterestimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tPinterest: " + person.pinterest)
    try:
        PinterestfinderObject.kill()
    except:
        print("Error Killing Pinterest Selenium instance")
    return peoplelist


def fill_twitter(peoplelist):
    TwitterfinderObject = twitterfinder.Twitterfinder(showbrowser)
    TwitterfinderObject.doLogin(twitter_username, twitter_password)
    if args.waitafterlogin:
        input("Press Enter to continue after verifying you are logged in...")

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True or args.debug == True:
            print("Twitter Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rTwitter Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = TwitterfinderObject.getTwitterProfiles(person.first_name, person.last_name)
                if args.debug == True:
                    print(profilelist)
            except:
                continue
        else:
            continue

        early_break = False
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            try:
                os.remove("potential_target_image.jpg")
            except:
                pass
            if early_break:
                break
            image_link = profilepic
            if image_link:
                try:
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if result < threshold:
                                person.twitter = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.twitterimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tTwitter: " + person.twitter)
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            if result < threshold:
                                updatedlist.append([profilelink, image_link, result])
                except:
                    continue
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.twitter = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.twitterimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tTwitter: " + person.twitter)
    try:
        TwitterfinderObject.kill()
    except:
        print("Error Killing Twitter Selenium instance")
    return peoplelist


def fill_instagram(peoplelist):
    InstagramfinderObject = instagramfinder.Instagramfinder(showbrowser)
    InstagramfinderObject.doLogin(instagram_username, instagram_password)
    if args.waitafterlogin:
        input("Press Enter to continue after verifying you are logged in...")

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True or args.debug == True:
            print("Instagram Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rInstagram Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        # if count == 3:
        #    print "triggered delete"
        #    InstagramfinderObject.testdeletecookies()
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = InstagramfinderObject.getInstagramProfiles(person.first_name, person.last_name,
                                                                         instagram_username, instagram_password)
                if args.debug == True:
                    print(profilelist)
            except:
                continue
        else:
            continue

        early_break = False
        # print "DEBUG: " + person.full_name
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            try:
                os.remove("potential_target_image.jpg")
            except:
                pass
            if early_break:
                break
            image_link = profilepic
            if image_link:
                try:
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if result < threshold:
                                person.instagram = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.instagramimage = encoding.smart_str(image_link, encoding='ascii',
                                                                           errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tInstagram: " + person.instagram)
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            if result < threshold:
                                # distance=result
                                updatedlist.append([profilelink, image_link, result])
                except Exception as e:
                    print("ERROR")
                    print(e)
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.instagram = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.instagramimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tInstagram: " + person.instagram)
    try:
        InstagramfinderObject.kill()
    except:
        print("Error Killing Instagram Selenium instance")
    return peoplelist


def fill_linkedin(peoplelist):
    LinkedinfinderObject = linkedinfinder.Linkedinfinder(showbrowser)
    LinkedinfinderObject.doLogin(linkedin_username, linkedin_password)
    if args.waitafterlogin:
        input("Press Enter to continue after verifying you are logged in...")

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True or args.debug == True:
            print("LinkedIn Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rLinkedIn Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        # if count == 3:
        # print "triggered delete"
        #    LinkedinfinderObject.testdeletecookies()
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = LinkedinfinderObject.getLinkedinProfiles(person.first_name, person.last_name,
                                                                       linkedin_username, linkedin_password)
                if args.debug == True:
                    print(profilelist)
            except:
                continue
        else:
            continue

        early_break = False
        # print "DEBUG: " + person.full_name
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            try:
                os.remove("potential_target_image.jpg")
            except:
                pass
            if early_break:
                break
            image_link = profilepic
            if image_link:
                try:
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if result < threshold:
                                person.linkedin = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.linkedinimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tLinkedIn: " + person.linkedin)
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            if result < threshold:
                                # distance=result
                                updatedlist.append([profilelink, image_link, result])
                except Exception as e:
                    print(e)
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.linkedin = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.linkedinimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tLinkedIn: " + person.linkedin)
    try:
        LinkedinfinderObject.kill()
    except:
        print("Error Killing LinkedIn Selenium instance")
    return peoplelist


def fill_vkontakte(peoplelist):
    VkontaktefinderObject = vkontaktefinder.Vkontaktefinder(showbrowser)
    VkontaktefinderObject.doLogin(vk_username, vk_password)
    if args.waitafterlogin:
        input("Press Enter to continue after verifying you are logged in...")

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True or args.debug == True:
            print("VKontakte Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rVKontakte Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = VkontaktefinderObject.getVkontakteProfiles(person.first_name, person.last_name)
                if args.debug == True:
                    print(profilelist)
            except:
                continue
        else:
            continue

        early_break = False
        # print "DEBUG: " + person.full_name
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            try:
                os.remove("potential_target_image.jpg")
            except:
                pass
            if early_break:
                break
            image_link = profilepic
            if image_link:
                try:
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if result < threshold:
                                person.vk = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.vkimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tVkontakte: " + person.vk)
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            if result < threshold:
                                # distance=result
                                updatedlist.append([profilelink, image_link, result])
                except Exception as e:
                    print(e)
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.vk = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.vkimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tVkontakte: " + person.vk)
    try:
        VkontaktefinderObject.kill()
    except:
        print("Error Killing VKontakte Selenium instance")
    return peoplelist


def fill_weibo(peoplelist):
    WeibofinderObject = weibofinder.Weibofinder(showbrowser)
    WeibofinderObject.doLogin(weibo_username, weibo_password)
    if args.waitafterlogin:
        input("Press Enter to continue after verifying you are logged in...")

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True or args.debug == True:
            print("Weibo Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rWeibo Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = WeibofinderObject.getWeiboProfiles(person.first_name, person.last_name)
                if args.debug == True:
                    print(profilelist)
            except:
                continue
        else:
            continue

        early_break = False
        # print "DEBUG: " + person.full_name
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            try:
                os.remove("potential_target_image.jpg")
            except:
                pass
            if early_break:
                break
            image_link = profilepic
            if image_link:
                try:
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if result < threshold:
                                person.weibo = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.weiboimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tWeibo: " + person.weibo)
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            if result < threshold:
                                # distance=result
                                updatedlist.append([profilelink, image_link, result])
                except Exception as e:
                    print(e)
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.weibo = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.weiboimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tWeibo: " + person.weibo)
    try:
        WeibofinderObject.kill()
    except:
        print("Error Killing Weibo Selenium instance")
    return peoplelist


def fill_douban(peoplelist):
    DoubanfinderObject = doubanfinder.Doubanfinder(showbrowser)
    DoubanfinderObject.doLogin(douban_username, douban_password)
    if args.waitafterlogin:
        input("Press Enter to continue after verifying you are logged in...")

    count = 1
    ammount = len(peoplelist)
    for person in peoplelist:
        if args.vv == True or args.debug == True:
            print("Douban Check %i/%i : %s" % (count, ammount, person.full_name))
        else:
            sys.stdout.write(
                "\rDouban Check %i/%i : %s                                " % (count, ammount, person.full_name))
            sys.stdout.flush()
        count = count + 1
        if person.person_image:
            try:
                target_image = face_recognition.load_image_file(person.person_image)
                target_encoding = face_recognition.face_encodings(target_image)[0]
                profilelist = DoubanfinderObject.getDoubanProfiles(person.first_name, person.last_name)
                if args.debug == True:
                    print(profilelist)
            except:
                continue
        else:
            continue

        early_break = False
        # print "DEBUG: " + person.full_name
        updatedlist = []
        for profilelink, profilepic, distance in profilelist:
            try:
                os.remove("potential_target_image.jpg")
            except:
                pass
            if early_break:
                break
            image_link = profilepic
            if image_link:
                try:
                    urllib.request.urlretrieve(image_link, "potential_target_image.jpg")
                    potential_target_image = face_recognition.load_image_file("potential_target_image.jpg")
                    try:  # try block for when an image has no faces
                        potential_target_encoding = face_recognition.face_encodings(potential_target_image)[0]
                    except:
                        continue
                    results = face_recognition.face_distance([target_encoding], potential_target_encoding)
                    for result in results:
                        if args.mode == "fast":
                            if result < threshold:
                                person.douban = encoding.smart_str(profilelink, encoding='ascii', errors='ignore')
                                person.doubanimage = encoding.smart_str(image_link, encoding='ascii', errors='ignore')
                                if args.vv == True:
                                    print("\tMatch found: " + person.full_name)
                                    print("\tDouban: " + person.douban)
                                early_break = True
                                break
                        elif args.mode == "accurate":
                            if result < threshold:
                                # distance=result
                                updatedlist.append([profilelink, image_link, result])
                except Exception as e:
                    print(e)
        if args.mode == "accurate":
            highestdistance = 1.0
            bestprofilelink = ""
            bestimagelink = ""
            for profilelink, image_link, distance in updatedlist:
                if distance < highestdistance:
                    highestdistance = distance
                    bestprofilelink = profilelink
                    bestimagelink = image_link
            if highestdistance < threshold:
                person.douban = encoding.smart_str(bestprofilelink, encoding='ascii', errors='ignore')
                person.doubanimage = encoding.smart_str(bestimagelink, encoding='ascii', errors='ignore')
                if args.vv == True:
                    print("\tMatch found: " + person.full_name)
                    print("\tDouban: " + person.douban)
    try:
        DoubanfinderObject.kill()
    except:
        print("Error Killing Douban Selenium instance")
    return peoplelist


# Login function for LinkedIn for company browsing (Credits to LinkedInt from MDSec)
def login():
    cookie_filename = "cookies.txt"
    cookiejar = http.cookiejar.MozillaCookieJar(cookie_filename)
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler(), urllib.request.HTTPHandler(debuglevel=0),
                                         urllib.request.HTTPSHandler(debuglevel=0),
                                         urllib.request.HTTPCookieProcessor(cookiejar))

    page = loadPage(opener, "https://www.linkedin.com/uas/login").decode('utf-8')
    parse = BeautifulSoup(page, "html.parser")
    csrf = ""
    for link in parse.find_all('input'):
        name = link.get('name')
        if name == 'loginCsrfParam':
            csrf = link.get('value')
    login_data = urllib.parse.urlencode(
        {'session_key': linkedin_username, 'session_password': linkedin_password, 'loginCsrfParam': csrf})
    page = loadPage(opener, "https://www.linkedin.com/checkpoint/lg/login-submit", login_data).decode('utf-8')

    parse = BeautifulSoup(page, "html.parser")
    cookie = ""
    try:
        cookie = cookiejar._cookies['.www.linkedin.com']['/']['li_at'].value
    except:
        print("Error logging in! Try changing language on social networks or verifying login data.")
        print(
            "If a capcha is required to login (due to excessive attempts) it will keep failing, try using a VPN or running with the -s flag to show the browser, where you can manually solve the capcha.")
        sys.exit(0)
    cookiejar.save()
    os.remove(cookie_filename)
    return cookie


def authenticate():
    try:
        a = login()
        print(a)
        session = a
        if len(session) == 0:
            sys.exit("[!] Unable to login to LinkedIn.com")
        print(("[*] Obtained new session: %s" % session))
        cookies = dict(li_at=session)
    except Exception as e:
        sys.exit("[!] Could not authenticate to LinkedIn. %s" % e)
    return cookies


def loadPage(client, url, data=None):
    try:
        if data is not None:
            try:
                response = client.open(url, data.encode("utf-8"))
            except:
                print("[!] Cannot load main LinkedIn GET page")
        else:
            try:
                response = client.open(url)
            except:
                print("[!] Cannot load main LinkedIn POST page")
        emptybyte = bytearray()
        return emptybyte.join(response.readlines())
    except:
        print("loadpage debug")
        traceback.print_exc()
        sys.exit(0)


# Setup Argument parser to print help and lock down options
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Social Mapper by Jacob Wilkin (Greenwolf)',
    usage='%(prog)s -f <format> -i <input> -m <mode> -t <threshold> <options>')
parser.add_argument('-v', '--version', action='version',
                    version='%(prog)s 0.1.0 : Social Mapper by Greenwolf (Github Link Here)')
parser.add_argument('-vv', '--verbose', action='store_true', dest='vv', help='Verbose Mode')
parser.add_argument('-d', '--debug', action='store_true', dest='debug', help='Debug Mode')
parser.add_argument('-f', '--format', action='store', dest='format', required=True,
                    choices=set(("csv", "imagefolder", "company", "socialmapper")),
                    help='Specify if the input file is either a \'company\',a \'CSV\',a \'imagefolder\' or a Social Mapper HTML file to resume')
parser.add_argument('-i', '--input', action='store', dest='input', required=True,
                    help='The name of the CSV file, input folder or company name to use as input')
parser.add_argument('-m', '--mode', action='store', dest='mode', required=True, choices=set(("accurate", "fast")),
                    help='Selects the mode either accurate or fast, fast will report the first match over the threshold while accurate will check for the highest match over the threshold')
parser.add_argument('-t', '--threshold', action='store', dest='thresholdinput', required=False,
                    choices=set(("loose", "standard", "strict", "superstrict")),
                    help='The strictness level for image matching, default is standard but can be specified to loose, standard, strict or superstrict')
parser.add_argument('-e', '--email', action='store', dest='email', required=False,
                    help='Provide an email format to trigger phishing list generation output, should follow a convention such as "<first><last><f><l>@domain.com"')
parser.add_argument('-cid', '--companyid', action='store', dest='companyid', required=False,
                    help='Provide an optional company id, for use with \'-f company\' only')

parser.add_argument('-s', '--showbrowser', action='store_true', dest='showbrowser',
                    help='If flag is set then browser will be visible')
parser.add_argument('-w', '--waitafterlogin', action='store_true', dest='waitafterlogin',
                    help='Wait for user to press Enter after login to give time to enter 2FA codes. Must use with -s')

parser.add_argument('-a', '--all', action='store_true', dest='a', help='Flag to check all social media sites')
parser.add_argument('-fb', '--facebook', action='store_true', dest='fb', help='Flag to check Facebook')
parser.add_argument('-pn', '--pinterest', action='store_true', dest='pin', help='Flag to check Pinterest')
parser.add_argument('-tw', '--twitter', action='store_true', dest='tw', help='Flag to check Twitter')
parser.add_argument('-ig', '--instagram', action='store_true', dest='ig', help='Flag to check Instagram')
parser.add_argument('-li', '--linkedin', action='store_true', dest='li',
                    help='Flag to check LinkedIn - Automatic with \'company\' input type')
parser.add_argument('-vk', '--vkontakte', action='store_true', dest='vk',
                    help='Flag to check the Russian VK VKontakte Site')
parser.add_argument('-wb', '--weibo', action='store_true', dest='wb', help='Flag to check the Chinese Weibo Site')
parser.add_argument('-db', '--douban', action='store_true', dest='db', help='Flag to check the Chinese Douban Site')

args = parser.parse_args()

