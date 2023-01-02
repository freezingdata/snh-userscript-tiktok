#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_api.py
@Time    :   2022/03/18
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2022, Freezingdata GmbH
@Desc    :   None
'''
import uuid

from snhwalker_utils import snhwalker, snh_major_version, snh_account_manager
import snhwalker_utils

from tiktok.tiktok_debug import *
from tiktok.tiktok_tools import getRegex
from urllib.parse import urlencode, parse_qs, urlparse
import requests
from requests.structures import CaseInsensitiveDict
import time
import sys

class TikTokAPI:
    def __init__(self, api_request = None):
        if not api_request is None:
            self.useragent = snhwalker_utils.snh_browser.GetJavascriptString('navigator.userAgent')
            print(api_request)
            self.cookies = getRegex(api_request["request_header_raw"], ";Cookie=(.*?);DNT", 1)
            self.universal_query = {
                "aid": 1988,
                "app_name": "tiktok_web",
                "device_platform": "web_mobile",
                "region": "DE",
                "priority_region": "",
                "os": "ios",
                "referer": "",
                "cookie_enabled": "true",
                "screen_width": 2304,
                "screen_height": 1440,
                "browser_language": "de",
                "browser_platform": "iPhone",
                "browser_name": "Mozilla",
                "browser_version": "5.0 (Windows)",
                "browser_online": "true",
                "timezone_name": "	Europe/Berlin",
                "is_page_visible": "true",
                "focus_state": "true",
                "is_fullscreen": "false",
                "history_len": 3,
                "language": "de",
                "msToken": parse_qs(urlparse(api_request["url"]).query)["msToken"][0]
            }
        pass

    def get_comments(self, aweme_id, count, cursor):
        query = {
                "count": count,
                "aweme_id": aweme_id,
                "cursor": cursor
                }   
        request_url = f'https://www.tiktok.com/api/comment/list/?{urlencode(self.universal_query)}&{urlencode(query)}' 
        return self.__get_request(request_url)

    def get_anwers(self, aweme_id, cid, count, cursor):
        query = {
                "count": count,
                "item_id": aweme_id,
                "comment_id": cid,
                "cursor": cursor
                }   
        request_url = f'https://www.tiktok.com/api/comment/list/reply/?{urlencode(self.universal_query)}&{urlencode(query)}' 
        return self.__get_request(request_url)        

    def __get_request(self, requesturl):
        debugPrint(f'[API] Request: {requesturl}')
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json, text/plain, */*"
        headers["Accept-Language"] = "de,en-US;q=0.7,en;q=0.3"
        headers["Referer"] = "https://www.tiktok.com/"
        headers["Connection"] = "keep-alive"
        headers["Cookie"] = self.cookies
        headers["Sec-Fetch-Dest"] = "empty"
        headers["Sec-Fetch-Mode"] = "no-cors"
        headers["Sec-Fetch-Site"] = "same-origin"
        headers["Pragma"] = "no-cache"
        headers["Cache-Control"] = "no-cache"
        headers["User-Agent"] = self.useragent
        try:
            resp = requests.get(requesturl, headers=headers)   
            debugWrite('TikTok_API_response_'+str(time.time())+'.data', resp.text)
            return resp.text     
        except Exception as e:
            debugPrint("'[API] ERROR in get_request")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            debugPrint(e, exc_type, exc_tb.tb_lineno)   
            return ''

    @staticmethod
    def do_simple_get_request(request_url):
        debugPrint("[API TikTok] - get request.")

        varname = f"xhr{str(uuid.uuid4().hex)[1:5]}"
        snhwalker_utils.snh_browser.ExecuteJavascript(f"delete {varname}Result;")
        snhwalker_utils.snh_browser.ExecuteJavascript(f"delete {varname};")
        snhwalker_utils.snh_browser.WaitMS(200)

        js = f"""var {varname} = new XMLHttpRequest();
                     {varname}.open("GET", "{request_url}", true); 
                     {varname}.withCredentials = true; 
                     {varname}.onload = function () {{{varname}Result = this.responseText}};
                     {varname}.send("");"""

        debugPrint(js)
        snhwalker_utils.snh_browser.ExecuteJavascript(js)
        snhwalker_utils.snh_browser.WaitMS(1500)

        result = snhwalker_utils.snh_browser.GetJavascriptString(f'{varname}Result;')
        count = 0
        while result == "" or count < 5:
            snhwalker_utils.snh_browser.WaitMS(1500)
            result = snhwalker_utils.snh_browser.GetJavascriptString(f'{varname}Result;')
            count += 1

        snhwalker_utils.snh_browser.ExecuteJavascript(f"let {varname}Result = '';")

        debugWrite("Tiktok_(" + str(time.time()) + ")_GetRequest.data", result)
        return result
