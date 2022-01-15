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