#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_urls.py
@Time    :   2022/01/06 18:25:00
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2021, Freezingdata GmbH
@Desc    :   None
'''
from typing import Union

import snhwalker_utils


def GetURL_OwnProfile():
    return 'https://www.tiktok.com/'

def GetURL_Profile(UserID, UserIDNumber = ''):
    return 'https://www.tiktok.com/@'+UserID

def GetURL_Friends(UserID, UserIDNumber = ''):
    return 'https://www.tiktok.com/'

def GetURL_Fotos(UserID, UserIDNumber = ''):
    return 'https://www.tiktok.com/@'+UserID

def GetURL_ProfileDetails(UserID, UserIDNumber = ''):
    return 'https://www.tiktok.com/'


class TiktokUrlSolver:
    TIKTOK_URL = "https://www.tiktok.com/"

    def __init__(self):
        self.page_type = self.solve_url_type()

    @classmethod
    def get_current_url(cls) -> str:
        return snhwalker_utils.snh_browser.GetJavascriptString('window.location.href')

    def solve_url_type(self) -> Union[str, None]:
        url = self.get_current_url()
        spited_url = url.split("/")

        if len(spited_url) == 4:
            if spited_url[3].startswith("@"):
                return "User"

        if len(spited_url) > 4:
            if "video" in spited_url[4]:
                return "Post"

        return None

    @classmethod
    def get_current_user_url(cls, url: str) -> str:
        return "/".join(url.split("/")[:4])
