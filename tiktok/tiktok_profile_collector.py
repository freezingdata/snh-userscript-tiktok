#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   tiktok_profile_collector.py
@Time    :   2022/01/06 18:30:12
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2021, Freezingdata GmbH
@Desc    :   None
"""

from tiktok.tiktok_tools import getRegex, checkJson
from tiktok.tiktok_debug import *
from tiktok.tiktok_captcha_resolver import TiktokCaptchaResolver
from snhwalker_utils import snhwalker, snh_major_version, snh_account_manager
import snhwalker_utils
import json


class TiktokProfileCollector:
    @staticmethod
    def current_is_user():
        Sourcecode = snhwalker.GetHTMLSource()
        jsonObjectStr = getRegex(Sourcecode, 'd="__NEXT_DATA__".*?>(.*?)</script>', 1)

        try:
            jsonObject = json.loads(jsonObjectStr)
            if jsonObject["page"] == '/share/user':
                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def current_is_page():
        # No community pages in TikTok
        return False

    @staticmethod
    def current_is_group():
        # No groups in TikTok
        return False

    @staticmethod
    def handle_profile():
        # returns the SNH Userdata Object of the current visible page
        userdata = snhwalker.CreateDictSNUserData()

        title_js = "document.querySelector('[data-e2e=user-subtitle]').textContent"
        title = snhwalker_utils.snh_browser.GetJavascriptString(title_js)
        userdata['UserName'] = title
        if userdata['UserName'] == '':
            title_js = "document.querySelector('h1[data-e2e=\"user-subtitle\"]').innerText"
            userdata['UserName'] = snhwalker_utils.snh_browser.GetJavascriptString(title_js)
        user_url_js = "document.querySelector('link[rel=\"canonical\"]').href;"
        userdata['UserURL'] = snhwalker_utils.snh_browser.GetJavascriptString(user_url_js)
        userdata['UserID'] = getRegex(userdata['UserURL'], '@(.*)', 1)

        HTML = snhwalker_utils.snh_browser.GetHTMLSource()
        userdata['UserIDNumber'] = getRegex(HTML, r'"authorId":"(\d+)', 1)

        user_profile_picture_js = "document.querySelector('[data-e2e=user-avatar] img').src"
        userdata['UserProfilePictureURL'] = snhwalker_utils.snh_browser.GetJavascriptString(user_profile_picture_js)
        userdata['ProfileType'] = 0
        debugPrint(userdata)
        snhwalker_utils.snhwalker.PromoteSNUserdata(userdata)

    @staticmethod
    def save_profile(profile_url):
        # loads a tiktok profile and submits the snh user objects to snh
        debugPrint(f'[INFO] Start save profile {profile_url}')
        snhwalker.StartResourceCapture('https://www.tiktok.com/api/user/detail', '')
        snhwalker.LoadPage(profile_url)

        break_counter = 0
        while True:
            snhwalker_utils.snh_browser.WaitMS(3000)
            TiktokCaptchaResolver(4)
            captured_data = snhwalker_utils.snh_browser.GetCapturedResource()
            if captured_data:
                break
            if break_counter > 5:
                debugPrint(f'[ERROR] Captured data is empty.')
                return

        snhwalker.StopResourceCapture()
        debugPrint(f'Profile Json: {captured_data}')
        if checkJson(captured_data):
            jsonObject = json.loads(captured_data)

            if "userInfo" not in jsonObject:
                return
            if "user" not in jsonObject["userInfo"]:
                return
            jsonObjectUser = jsonObject["userInfo"]["user"]

            userdata = snhwalker_utils.snh_model_manager.CreateDictSNUserData()  # Creates an empty SNUserData Dict
            userdata['UserName'] = jsonObjectUser["nickname"]
            userdata['UserID'] = jsonObjectUser["uniqueId"]
            userdata['UserIDNumber'] = jsonObjectUser["id"]
            userdata['UserURL'] = 'https://www.tiktok.com/@' + userdata['UserID']
            userdata['UserProfilePictureURL'] = jsonObjectUser["avatarLarger"]
            userdata['ProfileType'] = 0

            snhwalker.PromoteSNUserdata(userdata)
            debugPrint(f'[INFO] End save profile. Profile data: {userdata}')

            return userdata
