#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_posting_collector.py
@Time    :   2022/01/07 07:30:33
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2021, Freezingdata GmbH
@Desc    :   None
'''


from tiktok.tiktok_tools import getRegex, checkJson
from tiktok.tiktok_debug import *
from tiktok.tiktok_urls import *
from tiktok.tiktok_posting_html_creator import TiktokHTMLFactory
from tiktok.tiktok_timeline_comment_collector_api import TiktokCommentCollectorApi
from tiktok.tiktok_config import modul_config
from snhwalker_utils import snhwalker, snh_major_version, snh_account_manager
import snhwalker_utils
import json
import time
import datetime

class TiktokTimelineCollector:
    def __init__(self, profile, config):
        self.target_profile = profile
        self.config = config
        self.api_info = {
            "ownUserID": '',
            "destinationUserID": '',
            "verifyFp": ''
        }
        self.posting_list = []
        self.posting_count = 0
        self.captured_api_querys = []
        pass

    def run(self):
        debugPrint('[Timeline] Start saving timeline')
        profile_url = GetURL_Profile(self.target_profile["UserID"])

        # Capture the api call "item_list"
        snhwalker_utils.snh_browser.StartResourceCapture('www.tiktok.com/api/user/detail','');
        snhwalker_utils.snh_browser.LoadPage(profile_url)
        snhwalker_utils.snh_browser.WaitMS(2000)
        self.captured_api_querys = snhwalker_utils.snh_browser.CloseResourceCapture() # Needed for the potentiell cpmment querys
        debugPrint(f'[Timeline] {len(self.captured_api_querys)} API querys captured') 

        debugPrint(f'[Timeline] Get preloaded posting objects')
        page_json = self.__get_current_pagejson()
        debugWrite("Tiktok_(" + str(time.time()) + ")_preloaded_json_data.json", page_json) 
        debugPrint(f'[Timeline] Preloaded: {page_json[0:100]}')
        
        
        self.__handle_preloaded_postings(page_json)        
        self.__capture_postings() # TODO: Limit posting by config

        # Capture the complete post as html, if self.config["quick"] is False
        if modul_config["simple_timeline_collection"] is False:
            self.__enhanced_capturing()

        debugPrint('[Timeline] Finish saving timeline')


    def __enhanced_capturing(self):
        css_selector_post= 'div[class*=DivPlayerContainer]'
        css_selector_viewer = 'div[class*=DivBrowserModeContainer]'
        count_visible_posting = snhwalker_utils.snh_browser.GetJavascriptInteger(f'document.querySelectorAll("{css_selector_post}").length')   
        debugPrint(f'[Timeline] {count_visible_posting} posts found in DOM')

        snhwalker.InitProgress(count_visible_posting)

        # Iterates through all visible postings and click on each of it
        for idx in range(count_visible_posting):
            if idx < len(self.posting_list):
                snhwalker.StepProgress()                
                debugPrint(f'[Timeline] Open posts {idx+1}/{count_visible_posting}')  

                snhwalker_utils.snh_browser.ExecuteJavascript(f'document.querySelectorAll("{css_selector_post}")[{idx}].click();')   
                snhwalker_utils.snh_browser.WaitMS(2000)            
                self.posting_list[idx]['Sourcecode'] = snhwalker_utils.snh_browser.GetJavascriptString(f'document.querySelector("{css_selector_viewer}").outerHTML')
                self.posting_list[idx]['Stylesheet'] = snhwalker_utils.snh_browser.GetPageCSS() 
                self.send_to_snh(self.posting_list[idx])     

                # Start collection comments
                if len(self.captured_api_querys) > 0:
                    if self.config['SaveComments'] == True:
                        TiktokCommentCollectorApi(self.target_profile, self.posting_list[idx], self.captured_api_querys[0]).run()

    def __get_current_pagejson(self):
        return snhwalker_utils.snh_browser.GetJavascriptString("JSON.stringify(window['SIGI_STATE'])")

    
    def __handle_preloaded_postings(self, preloaded_json):
        # Extracts postings out of the json object, extracted from the HTML source code. 
        if not checkJson(preloaded_json):
            return
        
        page_data_object = json.loads(preloaded_json)

        if not "ItemModule" in page_data_object:
            return

        for key, tt_postingitem in page_data_object["ItemModule" ].items():
            self.ticktock_postingitem_handler(tt_postingitem)

    
    def __handle_captured_postings(self, captured_json):
        # Extracts postings out of the automatically loaded AJAX responses (https://m.tiktok.com/api/post/item_list/)
        if not checkJson(captured_json):
            return
        
        data_object = json.loads(captured_json)
        if not "itemList" in data_object:
            return

        for tt_postingitem in data_object["itemList" ]:
            self.ticktock_postingitem_handler(tt_postingitem)


    def __capture_postings(self):
        debugPrint('[Timeline] Scroll down complete timeline')
        snhwalker.DropStatusMessage('Scroll down complete timeline')
        snhwalker_utils.snh_browser.StartResourceCapture('https://m.tiktok.com/api/post/item_list/','')
        snhwalker_utils.snh_browser.ScrollPage()        
        api_querys = snhwalker_utils.snh_browser.CloseResourceCapture()   
        debugPrint('[Timeline] Begin extracting postings')
        for captured_request_item in  api_querys:
            debugWrite("Tiktok_(" + str(time.time()) + ")_posting_json_data.json", captured_request_item["response_body"])         
            self.__handle_captured_postings(captured_request_item["response_body"])     


    def ticktock_postingitem_handler(self, tt_postingitem):
        self.posting_count += 1
        debugPrint(f'[Timeline] Extracting post {self.posting_count}')
        snh_posting = self.ConvertToSNPostingdata(tt_postingitem)
        
        if modul_config["simple_timeline_collection"] is True:
            self.send_to_snh(snh_posting)
        else:
            self.posting_list.append(snh_posting)
       
    
    def send_to_snh(self, snh_posting):
        DTRangeStatus = snhwalker_utils.snh_model_manager.PostingDTStatus(snh_posting, self.config)
        if DTRangeStatus == 0:
            debugPrint(f'[Timeline]  - Post: create posting data {datetime.datetime.utcfromtimestamp(int(snh_posting["Timestamp"])).isoformat()}') 
            snhwalker.DropStatusMessage('Download images and videos in post: ' + datetime.datetime.utcfromtimestamp(int(snh_posting["Timestamp"])).isoformat())
            snhwalker.DownloadPostingFiles(snh_posting, 'https://www.tiktok.com')
            snhwalker.DropStatusMessage('Create screenshot: ' + datetime.datetime.utcfromtimestamp(int(snh_posting["Timestamp"])).isoformat())
            postingExists = snhwalker.PromoteSNPostingdata(snh_posting)                    
        

    def ConvertToSNPostingdata(self, TikTokItem):
        # create empty SNPostingdata Dict

        resultItem = snhwalker.CreateDictSNPostingdata()
        resultItem['PostingID_Network'] = TikTokItem['id']
        resultItem['Text'] = TikTokItem['desc']
        resultItem['Timestamp'] = TikTokItem['createTime']
        resultItem['Userdata'] = self.target_profile
        resultItem['CommentCount'] = TikTokItem['stats']['commentCount']
        resultItem['ReactionCount'] = TikTokItem['stats']['diggCount']
        resultItem['PostingURL'] = 'https://www.tiktok.com/@'+resultItem['Userdata']['UserID']+'/'+'video/'+resultItem['PostingID_Network']
        resultItem['VideoURL'] = TikTokItem['video']['playAddr']
        resultItem['PostingID'] = snhwalker.GetUniquePostingID(resultItem)

        if modul_config["simple_timeline_collection"]  is True:
            resultItem['Sourcecode'] = TiktokHTMLFactory().create_simple_posting(resultItem, TikTokItem)
            resultItem['Stylesheet'] = TiktokHTMLFactory().get_css_simple_posting()
        
        return resultItem




