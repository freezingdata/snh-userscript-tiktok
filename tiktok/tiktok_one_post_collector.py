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
from tiktok.tiktok_urls import TiktokUrlSolver
from tiktok.tiktok_debug import *
import re

from tiktok.tiktok_api import TikTokAPI
#from tiktok.tiktok_timeline_comment_collector_api import TiktokCommentCollectorApi
from tiktok.tiktok_timeline_comment_collector_scraping import TiktokCommentCollectorScraping
from tiktok.tiktok_captcha_resolver import TiktokCaptchaResolver
from tiktok.tiktok_posting_html_creator import TiktokHTMLFactory
from tiktok.tiktok_config import modul_config


class TiktokPostConverter:
    def __init__(self):
        pass

    def convert(self, TikTokItem, target_profile):
        resultItem = snhwalker_utils.snhwalker.CreateDictSNPostingdata()
        resultItem['PostingID_Network'] = TikTokItem['id']
        resultItem['Text'] = TikTokItem['desc']
        resultItem['Timestamp'] = TikTokItem['createTime']
        resultItem['Userdata'] = target_profile
        resultItem['CommentCount'] = TikTokItem['stats']['commentCount']
        resultItem['ReactionCount'] = TikTokItem['stats']['diggCount']
        resultItem['PostingURL'] = 'https://www.tiktok.com/@'+resultItem['Userdata']['UserID']+'/'+'video/'+resultItem['PostingID_Network']
        resultItem['VideoURL'] = TikTokItem['video']['playAddr']
        resultItem['PostingID'] = snhwalker_utils.snhwalker.GetUniquePostingID(resultItem)

        if modul_config["simple_timeline_collection"]  is True:
            resultItem['Sourcecode'] = TiktokHTMLFactory().create_simple_posting(resultItem, TikTokItem)
            resultItem['Stylesheet'] = TiktokHTMLFactory().get_css_simple_posting()
        
        return resultItem

class TiktokOnePostCollector:
    def __init__(self, url=None, config=None):
        self.url = url
        self.config = config if config else {}

    def save_post(self, ) -> dict:
        if not self.url:
            self.url = TiktokUrlSolver.get_current_url()
        snhwalker_utils.snh_browser.LoadPage(self.url)
        TiktokCaptchaResolver(4)

        debugPrint(f'[Timeline] Start saving post {self.url}')
        page_source: dict = self.get_page_source(self.url)
        snh_post: dict = self.get_post_data(page_source)
        TiktokCaptchaResolver(4)
        if snh_post:
            snhwalker_utils.snhwalker.DownloadPostingFiles(snh_post, 'https://www.tiktok.com')
            snhwalker_utils.snhwalker.PromoteSNPostingdata(snh_post)
            debugPrint(f'[Timeline] End saving post ')
            TiktokCaptchaResolver(4)
            if self.config.get('SaveComments'):
                debugPrint(f'[Timeline] Start save comments')
                current_user_url: str = TiktokUrlSolver.get_current_user_url(self.url)
                # captured_api_query: list = TiktokTimelineCollector.capture_api_queries(current_user_url)[0]
                #TiktokCommentCollectorApi(snh_post.get("Userdata"), snh_post, captured_api_query).run()
                TiktokCommentCollectorScraping(snh_post.get("Userdata"), snh_post, 'non_overlay').run()

            return snh_post

    # Handles the visible page as post and returns the basic posting data (without any media)
    # This function is just for posting detection purposes of the SNH1
    def handle_post(self, ) -> dict:
        if not self.url:
            self.url = TiktokUrlSolver.get_current_url()

        debugPrint(f'[Timeline] Start handling visible post {self.url}')
        page_source: dict = self.get_page_source(self.url)
             
        snh_post: dict = self.get_post_data(page_source)
        if snh_post:
            snhwalker_utils.snhwalker.PromoteSNPostingdata(snh_post)
        
    	    
    @staticmethod
    def get_page_source(current_url: str) -> dict:
        #snhwalker_utils.snh_browser.LoadPage(current_url)
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
        video_key = page_source.get("ItemList", {}).get("video", {}).get("keyword")
        source_path = page_source.get("ItemModule", {}).get(video_key)
        if source_path:
            snh_user = self.prepare_snh_user(source_path)
            snh_posting = self.prepare_snh_post(source_path, snh_user)
            snh_posting["Userdata"] = snh_user
            return snh_posting
        else:
            debugPrint("[ERROR] Source is empty")

    @staticmethod
    def prepare_snh_user(source: dict):
        debugPrint(f'[Timeline] Prepare snh user')

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
        return snh_user

    @staticmethod
    def prepare_snh_post(source: dict, snh_profile) -> dict:
        debugPrint(f'[Timeline] Prepare snh post')
        css_selector_viewer = 'div[class*=DivContentContainer]'
        snh_posting = TiktokPostConverter().convert(source, snh_profile)
        snh_posting['Sourcecode'] = snhwalker_utils.snh_browser.GetJavascriptString(f'document.querySelector("div[class*=DivPlayerContainer]").outerHTML') + \
                                    snhwalker_utils.snh_browser.GetJavascriptString(f'document.querySelector("div[class*=DivAuthorContainer]").outerHTML') +\
                                    snhwalker_utils.snh_browser.GetJavascriptString(f'document.querySelector("div[class*=PCommentTitle]").outerHTML')
                
        snh_posting['Stylesheet'] = snhwalker_utils.snh_browser.GetPageCSS()         
        #debugPrint(f'[Timeline] Prepared snh post {snh_posting}')
        return snh_posting
