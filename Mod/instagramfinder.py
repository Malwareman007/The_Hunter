from __future__ import print_function

import os
import sys
from time import sleep

from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class Instagramfinder(object):
    timeout = 10

    def __init__(self, showbrowser):
        if sys.platform == "darwin":
            display = Display(visible=0, size=(1600, 1024))
            display.start()
        opts = Options()
        if not showbrowser:
            os.environ['MOZ_HEADLESS'] = '1'
            opts.headless = True
        else:
            opts.headless = False
        firefoxprofile = webdriver.FirefoxProfile()
        firefoxprofile.set_preference("permissions.default.desktop-notification", 1)
        firefoxprofile.set_preference("dom.webnotifications.enabled", 1)
        firefoxprofile.set_preference("dom.push.enabled", 1)
        self.driver = webdriver.Firefox(firefox_profile=firefoxprofile, options=opts)

        self.driver.implicitly_wait(15)
        self.driver.delete_all_cookies()

    def doLogin(self, username, password):
        self.driver.get("https://www.instagram.com/accounts/login/?hl=en")
        # self.driver.get("https://instagram.com/accounts/login/")
        self.driver.execute_script('localStorage.clear();')	
	
        # convert unicode in instagram title to spaces for comparison
        titleString = ''.join([i if ord(i) < 128 else ' ' for i in self.driver.title])
		  if (titleString.startswith("Login")):                 
            print("\n[+] Instagram Login Page loaded successfully [+]")
            try:
                instagramUsername = self.driver.find_element_by_xpath("//input[@name='username']")
            except:
                print(
                    "Instagram Login Page username field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
            instagramUsername.send_keys(username)
            try:
                instagramPassword = self.driver.find_element_by_xpath("//input[@name='password']")
            except:
                print(
                    "Instagram Login Page password field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
            instagramPassword.send_keys(password)
            try:
                #self.driver.find_element_by_xpath("//button[contains(.,'Log In')]").click()
                self.driver.find_element_by_tag_name('form').submit()
            except:            	
                print(
                    "Instagram Login Page login button seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
            # self.driver.find_element_by_class_name("submit").click()
            # self.driver.find_element_by_css_selector("button.submit.btn.primary-btn").click()
            sleep(5)
            if (self.driver.title.encode('utf8', 'replace').startswith(bytes("Instagram", 'utf-8')) == True):
                print("[+] Instagram Login Success [+]\n")
                try:
                    # print("Closing \"Turn On Notifications\" message")
                    self.driver.find_element_by_class_name("aOOlW").click()
                    sleep(3)
                except:
                    # print("Closing Message Failed or did not exist")
                    pass
