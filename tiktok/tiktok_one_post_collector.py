#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_one_post_collector.py
@Time    :   2022/07/12 11:21:18
@Author  :   Anton Sinaiskii
@Contact :   as@freezingdata.de
@License :   (C)Copyright 2020-2022, Freezingdata GmbH
@Desc    :   None
'''

import json
import sys
import time

import snhwalker_utils
from tiktok.tiktok_debug import *
import re

from tiktok.tiktok_api import TikTokAPI
from tiktok.tiktok_timeline_comment_collector_api import TiktokCommentCollectorApi
from tiktok_timeline_collector import TiktokTimelineCollector


class TiktokOnePostCollector:
    def __init__(self, url=None, config=None):
        self.url = url
        self.config = config if config else {}

    def handle_post(self) -> dict:
        current_url = snhwalker_utils.snh_browser.GetJavascriptString("""window.location.href""")
        debugPrint(f'[Timeline] Start handle one_post {current_url}')
        print(f'[Timeline] Start handle one_post {current_url}')

        page_source: dict = self.get_page_source(current_url)
        snh_post: dict = self.get_post_data(page_source)
        snhwalker_utils.snhwalker.PromoteSNPostingdata(snh_post)

        debugPrint(f'[Timeline] End handle one_post {snh_post}')
        print(f'[Timeline] End handle one_post {snh_post}')

        if self.config.get('SaveComments'):
            debugPrint(f'[Timeline] Start save comments')
            print(f'[Timeline] Start save comments')
            TiktokCommentCollectorApi(snh_post.get("Userdata"), snh_post, None).run()

        return snh_post

    @staticmethod
    def get_page_source(current_url: str) -> dict:
        api_req = TikTokAPI().do_simple_get_request(current_url)
        re_data: list = re.findall(r'({"AppContext.+?})\<\/script\>', api_req, re.DOTALL)
        debugWrite("Tiktok_(" + str(time.time()) + ")_redata.data", re_data[0])
        try:
            page_source: dict = json.loads(re_data[0])
        except IndexError as e:
            page_source = {}
            debugPrint("[ERROR] Regex get nothing")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            debugPrint(e, exc_type, exc_tb.tb_lineno)
        except Exception as e:
            page_source = {}
            debugPrint("[ERROR] Unexpected error")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            debugPrint(e, exc_type, exc_tb.tb_lineno)
        return page_source

    def get_post_data(self, page_source: dict) -> dict:
        video_key = page_source.get("ItemList").get("video").get("keyword")
        source_path = page_source.get("ItemModule").get(video_key)

        snh_user = self.prepare_snh_user(source_path)
        snh_posting = self.prepare_snh_post(source_path, snh_user)
        snh_posting["Userdata"] = snh_user
        return snh_posting

    @staticmethod
    def prepare_snh_user(source: dict):
        debugPrint(f'[Timeline] Prepare snh user')
        print(f'[Timeline] Prepare snh user')

        snh_user = snhwalker_utils.snh_model_manager.CreateDictSNUserData()
        user_data = {
            "UserIDNumber": source.get("authorId"),
            "UserProfilePictureURL": source.get("avatarThumb"),
            "UserName": source.get("nickname"),
            "UserID": source.get("author"),
            "UserURL": f"https://www.tiktok.com/@{source.get('author')}",
        }
        snh_user.update(user_data)

        debugPrint(f'[Timeline] Prepared snh user {user_data}')
        print(f'[Timeline] Prepared snh user {user_data}')
        return snh_user

    @staticmethod
    def prepare_snh_post(source: dict, snh_profile) -> dict:
        debugPrint(f'[Timeline] Prepare snh post')
        print(f'[Timeline] Prepare snh post')

        snh_posting = TiktokTimelineCollector(snh_profile, None).ConvertToSNPostingdata(source)

        debugPrint(f'[Timeline] Prepared snh post {snh_posting}')
        print(f'[Timeline] Prepared snh post {snh_posting}')
        return snh_posting
