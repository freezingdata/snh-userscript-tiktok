#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_profile_collector.py
@Time    :   2022/01/06 18:30:12
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2021, Freezingdata GmbH
@Desc    :   None
'''


from tiktok.tiktok_tools import getRegex, checkJson
from tiktok.tiktok_debug import *
from tiktok.tiktok_captcha_resolver import TiktokCaptchaResolver
from snhwalker_utils import snhwalker, snh_major_version, snh_account_manager
import snhwalker_utils
import json

class TiktokProfileCollector:
    def __init__(self):
        pass

    def current_is_user(self):
        Sourcecode = snhwalker.GetHTMLSource()
        jsonObjectStr = getRegex(Sourcecode, 'd="__NEXT_DATA__".*?>(.*?)</script>',1)
        try:
            jsonObject = json.loads(jsonObjectStr)
            if ((jsonObject["page"] == '/share/user')):
                return True
            else:
                return False
        except:
            return False

    def current_is_page(self):
        # No community pages in TikTok
        return False

    def current_is_group(self):
        # No groups in TikTok
        return False

    def handle_profile(self):
        # returns the SNH Userdata Object of the current visible page
        userdata = snhwalker.CreateDictSNUserData()
        tempTitle = snhwalker_utils.snh_browser.GetJavascriptString("document.querySelector('meta[name=\"keywords\"]').content;")
        userdata['UserName'] = getRegex(tempTitle, '(.*?),',1)
        if userdata['UserName'] == '':
            userdata['UserName'] = snhwalker_utils.snh_browser.GetJavascriptString("document.querySelector('h1[data-e2e=\"user-subtitle\"]').innerText")
        userdata['UserURL'] = snhwalker_utils.snh_browser.GetJavascriptString("document.querySelector('link[rel=\"canonical\"]').href;")
        userdata['UserID'] = getRegex(userdata['UserURL'], '@(.*)',1)

        HTML = snhwalker_utils.snh_browser.GetHTMLSource()
        userdata['UserIDNumber'] = getRegex(HTML, '"authorId":"(\d+)',1)

        userdata['UserProfilePictureURL'] = snhwalker_utils.snh_browser.GetJavascriptString("document.querySelector('[data-e2e=user-avatar] img').src")
        userdata['ProfileType'] = 0
        debugPrint(userdata)
        snhwalker.PromoteSNUserdata(userdata)

    def save_profile(self, profile_url):
        # loads a tiktok profile and submits the snh user ojects to snh
        snhwalker.StartResourceCapture('https://www.tiktok.com/api/user/detail','');
        snhwalker.LoadPage(profile_url)
        snhwalker_utils.snh_browser.WaitMS(2000)  
        TiktokCaptchaResolver(4)
        snhwalker.StopResourceCapture()
        captured_data = snhwalker_utils.snh_browser.GetCapturedResource()
        debugPrint(f'Profile Json: {captured_data}')
        if checkJson(captured_data):
            jsonObject = json.loads(captured_data)

            if not "userInfo" in jsonObject:
                return
            if not "user" in jsonObject["userInfo"]:
                return     
            jsonObjectUser = jsonObject["userInfo"]["user"]       

            userdata = snhwalker.CreateDictSNUserData()  # Creats an empty SNUserData Dict
            userdata['UserName'] = jsonObjectUser["nickname"]
            userdata['UserID'] = jsonObjectUser["uniqueId"]
            userdata['UserIDNumber'] = jsonObjectUser["id"]
            userdata['UserURL'] = 'https://www.tiktok.com/@'+userdata['UserID']
            userdata['UserProfilePictureURL'] = jsonObjectUser["avatarLarger"]
            userdata['ProfileType'] = 0
            snhwalker.PromoteSNUserdata(userdata)
            return userdata

