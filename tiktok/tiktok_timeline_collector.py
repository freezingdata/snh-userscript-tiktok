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
#from tiktok.tiktok_timeline_comment_collector_api import TiktokCommentCollectorApi
from tiktok.tiktok_config import modul_config
from tiktok.tiktok_one_post_collector import TiktokOnePostCollector, TiktokPostConverter
from tiktok.tiktok_captcha_resolver import TiktokCaptchaResolver
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
        self.captured_api_queries = []
        pass

    def run(self):
        debugPrint('[Timeline] Start saving timeline')
        profile_url = GetURL_Profile(self.target_profile["UserID"])
        # Capture the api call "item_list"
        self.captured_api_queries = self.capture_api_queries(profile_url)
        debugPrint(f'[Timeline] {len(self.captured_api_queries)} API querys captured')

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

        #Count postings to collect
        collect_count = 0
        for posting_item in self.posting_list:
            DTRangeStatus = snhwalker_utils.snh_model_manager.PostingDTStatus(posting_item, self.config)
            if DTRangeStatus == 0:    
                collect_count += 1    

        snhwalker_utils.snhwalker.InitProgress(collect_count)
        for idx, posting_item in enumerate(self.posting_list):
            DTRangeStatus = snhwalker_utils.snh_model_manager.PostingDTStatus(posting_item, self.config)
            if DTRangeStatus == 0:
                debugPrint(f'[Timeline] Open posts {idx+1}/{count_visible_posting}')  
                snhwalker_utils.snhwalker.StepProgress()    
                TiktokOnePostCollector(posting_item["PostingURL"], self.config).save_post()


        # Iterates through all visible postings and click on each of it
        """
        for idx in range(count_visible_posting):
            if idx < len(self.posting_list):
                snhwalker_utils.snhwalker.StepProgress()                
                debugPrint(f'[Timeline] Open posts {idx+1}/{count_visible_posting}')  

                snhwalker_utils.snh_browser.ExecuteJavascript(f'document.querySelectorAll("{css_selector_post}")[{idx}].click();')   
                snhwalker_utils.snh_browser.WaitMS(2000)            
                self.posting_list[idx]['Sourcecode'] = snhwalker_utils.snh_browser.GetJavascriptString(f'document.querySelector("{css_selector_viewer}").outerHTML')
                self.posting_list[idx]['Stylesheet'] = snhwalker_utils.snh_browser.GetPageCSS() 
                self.send_to_snh(self.posting_list[idx])     

                # Start collection comments
                if len(self.captured_api_queries) > 0:
                    if self.config['SaveComments'] == True:
                        TiktokCommentCollectorApi(self.target_profile, self.posting_list[idx], self.captured_api_queries[0]).run()
        """

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

        if data_object.get("itemList"):
            for tt_postingitem in data_object.get("itemList"):
                self.ticktock_postingitem_handler(tt_postingitem)


    def __capture_postings(self):
        debugPrint('[Timeline] Scroll down complete timeline')
        snhwalker_utils.snhwalker.DropStatusMessage('Scroll down complete timeline')
        debugPrint('[Timeline] Capture: https://www.tiktok.com/api/')
        snhwalker_utils.snh_browser.StartResourceCapture('api','')


        snhwalker_utils.snh_browser.ScrollPage()        
        ScrollTime = time.time()    
        ScrollPointY = snhwalker_utils.snh_browser.GetJavascriptInteger('window.scrollY ')
        while ((time.time() - ScrollTime) < 2):
            TiktokCaptchaResolver(4)
            snhwalker_utils.snh_browser.ExecuteJavascript('window.scrollBy(0, 10000) ')
            snhwalker_utils.snh_browser.WaitMS(1500)
            ScrollPoint1Y = snhwalker_utils.snh_browser.GetJavascriptInteger('window.scrollY ')
            if (ScrollPoint1Y > ScrollPointY):
                ScrollTime = time.time()
                ScrollPointY = ScrollPoint1Y   


        api_querys = snhwalker_utils.snh_browser.CloseResourceCapture()  
        debugPrint(f'[Timeline] {len(api_querys)} API querys captured')  
        debugPrint('[Timeline] Begin extracting postings')
        count = 1
        for captured_request_item in  api_querys:
            debugPrint(f'[Timeline] Handle API Query ({count}/{len(api_querys)})')  
            count += 1
            debugWrite("Tiktok_(" + str(time.time()) + ")_posting_json_data.json", captured_request_item["response_body"])         
            self.__handle_captured_postings(captured_request_item["response_body"])     


    def ticktock_postingitem_handler(self, tt_postingitem):
        self.posting_count += 1
        debugPrint(f'[Timeline] Extracting post {self.posting_count}')
        snh_posting = TiktokPostConverter().convert(tt_postingitem, self.target_profile)
        
        if modul_config["simple_timeline_collection"] is True:
            self.send_to_snh(snh_posting)
        else:
            self.posting_list.append(snh_posting)
       
    
    def send_to_snh(self, snh_posting):
        DTRangeStatus = snhwalker_utils.snh_model_manager.PostingDTStatus(snh_posting, self.config)
        if DTRangeStatus == 0:
            debugPrint(f'[Timeline]  - Post: create posting data {datetime.datetime.utcfromtimestamp(int(snh_posting["Timestamp"])).isoformat()}') 
            snhwalker_utils.snhwalker.DropStatusMessage('Download images and videos in post: ' + datetime.datetime.utcfromtimestamp(int(snh_posting["Timestamp"])).isoformat())
            snhwalker_utils.snhwalker.DownloadPostingFiles(snh_posting, 'https://www.tiktok.com')
            snhwalker_utils.snhwalker.DropStatusMessage('Create screenshot: ' + datetime.datetime.utcfromtimestamp(int(snh_posting["Timestamp"])).isoformat())
            postingExists = snhwalker.PromoteSNPostingdata(snh_posting)                    
        

    @classmethod
    def capture_api_queries(cls, url: str) -> list:
        debugPrint('[Timeline] Capture: www.tiktok.com/api/user/detail')
        snhwalker_utils.snh_browser.StartResourceCapture('www.tiktok.com/api/user/detail', '')
        snhwalker_utils.snh_browser.LoadPage(url)
        snhwalker_utils.snh_browser.WaitMS(2000)
        # Needed for the potentiell comment queries
        return snhwalker_utils.snh_browser.CloseResourceCapture()



