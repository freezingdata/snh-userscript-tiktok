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
import json

from snhwalker_utils import snhwalker, snh_major_version, snh_account_manager
import snhwalker_utils

class TiktokCommentCollectorApi:
    def __init__(self, profile, posting):
        self.target_profile = profile
        self.target_posting = posting   
        self.isInitialized = False
        self.counter = 0
        requests = snhwalker_utils.snh_browser.FlushResourceCapture()
        if len(requests) > 0:   
            self.isInitialized = True
            self.api = TikTokAPI(requests[0])    
        pass

    def run(self):
        if self.isInitialized  is False:
            debugPrint(f'[Timeline Comments] No API calls captured, abord comment collection')    
            return
        self.__get_comments()        
        

    def __get_comments(self):
        # Collects the first level comments of the postings comment list. 
        pagination = {
                "more_pages_to_load": True,
                "cursor": 0,
                "total": 0,
            }
        while pagination["more_pages_to_load"] is True:
            jsonstring = self.api.get_comments(self.target_posting['PostingID_Network'], 20, pagination["cursor"])
            if checkJson(jsonstring) is False:
                break

            api_response_body = json.loads(jsonstring)
            api_converter = TiktokAPIConverter(api_response_body)

            if not api_converter.isCommentlist():
                debugPrint(f'[Timeline Comments] The API response is not comment related')  
                break
            pagination = api_converter.getPagination()
            self.__converting_comment_api_responses(api_converter)

            if (modul_config["limit_root_comments"] is True) and ((pagination["cursor"]) >= modul_config["limit_root_comment_count"]):
                debugPrint(f'[Timeline Comments] Collection of root comments limit of {modul_config["limit_root_comment_count"] } comments reached - finish scroll process')  
                break                  

            snhwalker_utils.snh_browser.WaitMS(500)    


    def __handle_comment_as_friendship(self, comment: dict) -> None:                
        SNHFriendItem = snhwalker_utils.snh_model_manager.CreateDictSNFriendshipdata()
        SNHFriendItem['User'] = comment['User']
        SNHFriendItem['FriendshipType'] = 'FTComment' 
        snhwalker.PromoteSNFriendshipdata(SNHFriendItem)  


    def __converting_comment_api_responses(self, api_response) -> None:
        # converts the api response of the "get_comments" query and handles the appearence of 
        # comment answers
        api_comment_list =  api_response.asTiktok_comment_list()
        if api_comment_list is None:
            return

        for idx, apicomment in enumerate(api_comment_list):
            # Iterate though all comments inside the comment response
            api_converter_comment = TiktokAPIConverter(apicomment)
            snh_comment = api_converter_comment.asSNHCommentdata(False, self.target_posting["PostingID"], 0)

            if snh_comment is None:
                continue

            self.counter  += 1        
            snhwalker.DropStatusMessage(f'Converting comments ({self.counter}|{self.target_posting["PostingID"]})')
            snhwalker.PromoteSNCommentdata(snh_comment)   
            self.__handle_comment_as_friendship(snh_comment) 

            debugPrint(f'Converting comments ({self.counter}|{self.target_posting["PostingID"]})')  
            if (modul_config["load_comment_answers"] is False):
                continue

            if (modul_config["limit_comment_answers"] is True) and (self.counter > modul_config["limit_comment_answers_count"]):
                continue
            
            self.__collect_ansers(api_converter_comment, snh_comment)

                           
    def __collect_ansers(self, api_converter_comment: TiktokAPIConverter, snh_comment: dict) -> None:
        # Collects the answers of the given comment
        answerList = api_converter_comment.getCommentsAnswers()
        max_count_answers = api_converter_comment.getCommentAnswerCount()
        if max_count_answers > len(answerList):
            cursor = len(answerList)
            answer_load_count = 10
            while True:
                debugPrint(f'[Timeline Comments] Load answers of {snh_comment["__tiktokid__"]} - {cursor}/{max_count_answers}')  
                if cursor > max_count_answers:
                    break

                jsonstring = self.api.get_anwers(self.target_posting['PostingID_Network'], snh_comment["__tiktokid__"], answer_load_count, cursor)
                if checkJson(jsonstring) is False:
                    break

                api_response_body = json.loads(jsonstring)    
                api_converter_answerlist = TiktokAPIConverter(api_response_body)

                if not api_converter_answerlist.isCommentlist():
                    debugPrint(f'[Timeline Comments] The API response is not comment related')  
                    break

                answerList += api_converter_answerlist.asTiktok_comment_list()
                cursor += answer_load_count
                snhwalker_utils.snh_browser.WaitMS(500)    
            
        for answer in answerList:
            api_converter_answer = TiktokAPIConverter(answer)
            snh_comment_answer = api_converter_answer.asSNHCommentdata(True, self.target_posting["PostingID"], snh_comment["CommentID"])    
            if snh_comment_answer is None:
                continue

            snhwalker.DropStatusMessage(f'Converting comments ({self.counter }|{self.target_posting["PostingID"]})')
            
            snhwalker.PromoteSNCommentdata(snh_comment_answer)    
            self.__handle_comment_as_friendship(snh_comment_answer)  



