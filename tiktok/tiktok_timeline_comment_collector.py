from email import header

#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_timeline_comment_collector.py
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
from tiktok.tiktok_config import modul_config
import json
import time
import datetime

from snhwalker_utils import snhwalker, snh_major_version, snh_account_manager
import snhwalker_utils

class TiktokCommentCollector:
    def __init__(self, profile, posting):
        self.target_profile = profile
        self.target_posting = posting    
        self.currentURL = snhwalker_utils.snh_browser.GetJavascriptString(f'window.location.href')    

        self.css_rootComments = 'div[class*=DivCommentListContainer] > div[class*=DivCommentItemContainer]'
        self.css_comment_panel = 'div[class*=DivCommentListContainer]'
        self.css_comment_loadmore = '[data-e2e*=view-more] > svg'
        self.css_comment_loadmore_click = '[data-e2e*=view-more]'
        self.css_isloading = '[class*=DivReplyActionContainer] > svg'

        self.comment_list = []
        self.api_request_list = []
        self.counter = 0
        pass


    def run(self):
        debugPrint(f'[Timeline Comments] Start collecting comments for posting {self.target_posting["PostingID"]}')

        if not "/video/" in self.currentURL:
            debugPrint(f'[Timeline Comments] The current page is not a video / posting page ({self.currentURL})')    
            return

        if self.comments_posted() is False:
            debugPrint(f'[Timeline Comments] There are no comments to collect')    
            return    

        # Start collecting comments
        self.collect_comments()        

        debugPrint(f'[Timeline Comments] Collection completed')


    def get_comment_from_list(self, userid, text):
        # searches vor a specific comment inside the list self.comment_list and returns
        # it. If the comment doesn't exists in the list, return value is "None" 
        for comment in self.comment_list:
            if comment["Answer"] is True:
                continue
            if not comment["User"]["UserID"] == userid:
                continue  
            if not comment["Content"] == text:
                continue  
            return comment
        return None                     


    def get_rootComments_count(self):
        # return the count of first level comments, which are currently visible beside the posting. 
        return snhwalker_utils.snh_browser.GetJavascriptInteger(f'document.querySelectorAll("{self.css_rootComments}").length')


    def comments_posted(self):
        # returns a boolean value
        # True: currently, there are comments visible
        # False: currently, there are no
        rootComments_count = self.get_rootComments_count()    
        return rootComments_count > 0


    def converting_comment_api_responses(self, isAnswer, root_comment_id = 0):
        request_list = self.api_request_list + snhwalker_utils.snh_browser.FlushResourceCapture() 
        self.api_request_list = []
        
        for request_item in request_list:

            # iterate though all captured API request
            debugWrite("Tiktok_(" + str(time.time()) + ")_commentlist.json", request_item["response_body"]) 

            # Checking,if its a api comment response
            if checkJson(request_item["response_body"]) is False:
                continue

            api_response_body = json.loads(request_item["response_body"])
            api_converter = TiktokAPIConverter(api_response_body)
            if not api_converter.isCommentlist():
                debugPrint(f'[Timeline Comments] The API call {request_item["url"]} is not comment related')  
                continue

            api_comment_list =  api_converter.asTiktok_comment_list()
            if api_comment_list is None:
                continue

            for apicomment in api_comment_list:
                # Tterate though all comments inside the comment response
                snh_comment = TiktokAPIConverter(apicomment).asSNHCommentdata(isAnswer, self.target_posting["PostingID"], root_comment_id)

                if snh_comment is None:
                    continue
                if (modul_config["limit_root_comments"] is True) and (modul_config["limit_root_comment_count"] < len(self.comment_list)):
                    break

                self.counter  += 1        
                snhwalker.DropStatusMessage(f'Converting comments ({self.counter }|{self.target_posting["PostingID"]})')
                self.comment_list += [snh_comment]                 
                snhwalker.PromoteSNCommentdata(snh_comment)     

            if isAnswer is True:
                continue

            if (modul_config["limit_root_comments"] is True) and (modul_config["limit_root_comment_count"] < len(self.comment_list)):
                debugPrint(f'[Timeline Comments] Collection of  comments - limit of {modul_config["limit_root_comment_count"] } comments reached')  
                return  

    def count_comment_calls(self):
        result = 0
        for request_item in self.api_request_list:
            if "comments" in request_item["response_body"]:
                result += 1
        return result

    def scroll_comment_panel(self):
        # Scrolls the comment panel, until it reaches the last comment (depending on the reload time) or
        # the count of potential root comments reaches the value inside the modul configuration
        dom = f'document.querySelector("{self.css_comment_panel}")'
        ScrollTime = time.time()
        ScrollPointY = snhwalker_utils.snh_browser.GetJavascriptInteger(dom+ '.scrollTop')
        while (time.time() - ScrollTime) < 2:
            snhwalker_utils.snh_browser.WaitMS(100)
            snhwalker_utils.snh_browser.ExecuteJavascript(dom + '.scrollTop +=10000')
            ScrollPoint1Y = snhwalker_utils.snh_browser.GetJavascriptInteger(dom + '.scrollTop')
            if (ScrollPoint1Y > ScrollPointY):
                ScrollTime = time.time()
                ScrollPointY = ScrollPoint1Y   

                self.api_request_list += snhwalker_utils.snh_browser.FlushResourceCapture()
                count_calls = self.count_comment_calls()
                snhwalker.DropStatusMessage(f'Scrolling comment ({count_calls*20})')
                if (modul_config["limit_root_comments"] is True) and (modul_config["limit_root_comment_count"] < ((count_calls-2) * 20)):
                    debugPrint(f'[Timeline Comments] Collection of root comments limit of {modul_config["limit_root_comment_count"] } comments reached - finish scroll process')  
                    break


    def collect_comments(self):
        debugPrint(f'[Timeline Comments] Scroll down the comments')  
        snhwalker.DropStatusMessage('Handling comments')

        # Scroll down the complete comment panel
        self.scroll_comment_panel()

        # get all comment related JSON documents
        snhwalker.DropStatusMessage('Converting root comments')
        
        debugPrint(f'[Timeline Comments] Converting root comments')  

        self.counter = 0
        self.converting_comment_api_responses(False)

        # load all answers to comments by clicking at the "load more" buttons
        if modul_config["load_comment_answers"] is True:
            self.collect_comment_anwers()


    def more_answers_to_load(self, comment_idx):
        return snhwalker_utils.snh_browser.GetJavascriptInteger(f'document.querySelectorAll("{self.css_rootComments}")[{comment_idx}].querySelectorAll("{self.css_comment_loadmore}").length') > 0


    def answer_is_loading(self, comment_idx):
        return snhwalker_utils.snh_browser.GetJavascriptInteger(f'document.querySelectorAll("{self.css_rootComments}")[{comment_idx}].querySelectorAll("{self.css_isloading}").length') > 0


    def load_more_answers(self, comment_idx):
        snhwalker_utils.snh_browser.ExecuteJavascript(f'document.querySelectorAll("{self.css_rootComments}")[{comment_idx}].querySelector("{self.css_comment_loadmore_click}").click();')
        snhwalker_utils.snh_browser.WaitMS(500)

        #max 5 secs do load answers, to avoid borwser freezings
        timerData = time.time() 
        while (self.answer_is_loading(comment_idx) is True) and ((time.time() - timerData) < 5):
            snhwalker_utils.snh_browser.WaitMS(500)    
        return ((time.time() - timerData) < 5)
        


    def collect_comment_anwers(self):
        rootComments_count = self.get_rootComments_count()
        if modul_config["limit_comment_answers_count"] <  rootComments_count:
            rootComments_count = modul_config["limit_comment_answers_count"] 

        for c_count in range(rootComments_count):

            if self.more_answers_to_load(c_count) is True:
                # Get the correct comment from the collected list
                # In the HTML code, theres no comment id, so we have to 
                # guess the correct comment by username and text content
                rootComment_dom = f'document.querySelectorAll("{self.css_rootComments}")[{c_count}]'  
                temp_username = snhwalker_utils.snh_browser.GetJavascriptString(f'{rootComment_dom}.querySelector("a[class*=StyledUserLinkName]").href').replace("https://www.tiktok.com/@","")
                temp_text = snhwalker_utils.snh_browser.GetJavascriptString(f'{rootComment_dom}.querySelector("[data-e2e=comment-level-1]").innerText')
                current_comment = self.get_comment_from_list(temp_username, temp_text)
                if current_comment is None:
                    debugPrint(f'[Timeline Comments] DOM comment not found in  list ({temp_username},{temp_text})')  
                    continue

                # Loading of the comment answers
                load_count = 0 # Just for output purposes
                while self.more_answers_to_load(c_count) is True:
                    load_count  += 1
                    debugPrint(f'[Timeline Comments] Load more comment answers for comment {c_count}/{load_count}')  
                    if self.load_more_answers(c_count) is False:
                        break

                debugPrint(f'[Timeline Comments] Converting answers of comment  {c_count}')  
                # Extracting the comment from the collected API calls
                self.converting_comment_api_responses(True, current_comment["CommentID"])


