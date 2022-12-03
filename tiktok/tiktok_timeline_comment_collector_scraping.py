#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_timeline_comment_collector_api.py
@Time    :   2022/03/18
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2022, Freezingdata GmbH
@Desc    :   None
'''

from tiktok.tiktok_tools import getRegex, checkJson, scrollDOM
from tiktok.tiktok_debug import *
from tiktok.tiktok_urls import *
from tiktok.tiktok_api_converter import TiktokAPIConverter
from tiktok.tiktok_api import TikTokAPI
from tiktok.tiktok_config import modul_config
from tiktok.tiktok_captcha_resolver import TiktokCaptchaResolver
import json
import time

from snhwalker_utils import snhwalker, snh_major_version, snh_account_manager
import snhwalker_utils



class TiktokCommentCollectorScraping:
    def __init__(self, profile, posting, html_type):
        self.target_profile = profile
        self.target_posting = posting   
        self.isInitialized = False
        self.counter = 0
        self.html_type = html_type
        self.comments_1lv = []
        self.snh_comments = []
        if html_type == 'overlay':    
            self.css_selector = {
                    'comment_panel': 'div[class*=DivCommentListContainer]',
                    'comment_item':  'div[class*=DivCommentItemContainer]'
                }   
        else:
            self.css_selector = {
                    'comment_panel': '',
                    'comment_item':  'div[class*=DivCommentItemContainer]',
                    'reply_loader': 'p[class*=PReplyActionText]'
                }                    
        pass

    def run(self):
        if self.html_type == 'non_overlay':  
            self.__comments_1lv_nOverlay()   
            self.__handle_1lv_comments()   
            self.__comments_2lv_nOverlay()  

    def __comments_2lv_nOverlay(self):    
        debugPrint(f'[Timeline Comments] Loading answers')
        snhwalker_utils.snh_browser.WaitMS(3000)
        dom_comment_item_list = f'document.querySelectorAll("{self.css_selector["comment_item"]}")'
        dom_reply_loader = f'querySelectorAll("{self.css_selector["reply_loader"]}")'

        
        for idx, snh_comment_1lv_item in enumerate(self.snh_comments):    
            if idx < modul_config["limit_root_comment_count"]:        
                #debugPrint(f'{dom_comment_item_list}[{idx}].{dom_reply_loader}.length')
                answer_request_count = 0
                answers_to_load = snhwalker_utils.snh_browser.GetJavascriptInteger(f'{dom_comment_item_list}[{idx}].{dom_reply_loader}.length') > 0
                if answers_to_load == False:
                    continue
                snhwalker_utils.snh_browser.StartResourceCapture("api/comment/list/reply", "")  
                while answers_to_load:
                    TiktokCaptchaResolver(4)
                    answer_request_count += 1
                    debugPrint(f'[Timeline Comments] Prepare to laod answers from comment - {idx},{answer_request_count} / max {len(self.snh_comments)} ')                  
                    snhwalker_utils.snh_browser.ExecuteJavascript(f'{dom_comment_item_list}[{idx}].{dom_reply_loader}[0].scrollIntoView();]')   
                    snhwalker_utils.snh_browser.ExecuteJavascript(f'{dom_comment_item_list}[{idx}].{dom_reply_loader}[0].click();')   
                    #debugPrint(f'{dom_comment_item_list}[{idx}].{dom_reply_loader}.length')
                    snhwalker_utils.snh_browser.WaitMS(1000)
                    answers_to_load = snhwalker_utils.snh_browser.GetJavascriptInteger(f'{dom_comment_item_list}[{idx}].{dom_reply_loader}.length') > 0
                
                resource_capture_anwers: list = snhwalker_utils.snh_browser.CloseResourceCapture()   
                debugWrite("Tiktok_(" + str(time.time()) + ")_comments_answers.data", json.dumps(resource_capture_anwers))
                self.__decode_answers(resource_capture_anwers, snh_comment_1lv_item)                   
    
    
    def __comments_1lv_nOverlay(self):
        # reload is necessary, becuase the first comments have allready been displayed without capturing
        
        snhwalker_utils.snh_browser.ExecuteJavascript('location.reload();')      
        snhwalker_utils.snh_browser.StartResourceCapture("api/comment/list", "")  
        snhwalker_utils.snh_browser.WaitMS(3000)
        TiktokCaptchaResolver(4)

        # Scroll comments, until 100 1lv comments are visible
        debugPrint(f'[Timeline Comments] Collection of root comments limit of {modul_config["limit_root_comment_count"] } comments reached - finish scroll process')  

        ScrollTime = time.time()
        item_count = 0      
        dom_comment_item_list = f'document.querySelectorAll("{self.css_selector["comment_item"]}")'
        ScrollPointY = snhwalker_utils.snh_browser.GetJavascriptInteger('window.scrollY ')
        while ((time.time() - ScrollTime) < 2) and (item_count < modul_config["limit_root_comment_count"]):
            TiktokCaptchaResolver(4)
            item_count = snhwalker_utils.snh_browser.GetJavascriptInteger(dom_comment_item_list + '.length')
            debugPrint(f'[Timeline Comments] Collection of root comments - {item_count} / max {modul_config["limit_root_comment_count"] } ')  
            snhwalker_utils.snh_browser.ExecuteJavascript('window.scrollBy(0, 10000) ')
            snhwalker_utils.snh_browser.WaitMS(1500)
            ScrollPoint1Y = snhwalker_utils.snh_browser.GetJavascriptInteger('window.scrollY ')
            
            if (ScrollPoint1Y > ScrollPointY):
                ScrollTime = time.time()
                ScrollPointY = ScrollPoint1Y            
        debugPrint(f'[Timeline Comments] Collection of root comments finished: {item_count} ')  
        resource_capture_1lvcomments: list = snhwalker_utils.snh_browser.CloseResourceCapture()   
        debugWrite("Tiktok_(" + str(time.time()) + ")_comments_1lv.data", json.dumps(resource_capture_1lvcomments))
        self.__decode_1lv_comments(resource_capture_1lvcomments)        
            
    def __decode_1lv_comments(self, rescource_capture):
        for capture_item in rescource_capture:        
            if checkJson(capture_item["response_body"]):     
                commentlist_json: dict = json.loads(capture_item["response_body"])
                for comment in commentlist_json["comments"]:
                    self.comments_1lv.append(comment) 
        debugWrite("Tiktok_(" + str(time.time()) + ")_comments_1lv.json", json.dumps(self.comments_1lv)) 

    def __handle_1lv_comments(self):
        for comment_1lv_item in self.comments_1lv:
            self.counter += 1
            api_converter_comment = TiktokAPIConverter(comment_1lv_item)
            snh_comment = api_converter_comment.asSNHCommentdata(False, self.target_posting["PostingID"], 0)     
            self.snh_comments.append(snh_comment)      
            snhwalker.DropStatusMessage(f'[Timeline Comments] Converting comments ({self.counter}|{self.target_posting["PostingID"]})')
            if self.counter <= modul_config["limit_root_comment_count"]:
                snhwalker.PromoteSNCommentdata(snh_comment)  

    def __decode_answers(self, rescource_capture, snh_root_comment):
        for capture_item in rescource_capture:        
            if checkJson(capture_item["response_body"]):     
                commentlist_json: dict = json.loads(capture_item["response_body"])
                for comment in commentlist_json.get("comments", []):
                    api_converter_comment = TiktokAPIConverter(comment)
                    snh_comment = api_converter_comment.asSNHCommentdata(False, self.target_posting["PostingID"], snh_root_comment['CommentID'] )                        
                    snhwalker.PromoteSNCommentdata(snh_comment)  
        debugWrite("Tiktok_(" + str(time.time()) + ")_comments_1lv.json", json.dumps(self.comments_1lv))         