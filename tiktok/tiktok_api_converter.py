#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_api_converter.py
@Time    :   2022/03/18
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2022, Freezingdata GmbH
@Desc    :   None
'''


from tiktok.tiktok_tools import getRegex, checkJson
from tiktok.tiktok_debug import *
from tiktok.tiktok_urls import *
from snhwalker_utils import snhwalker, snh_major_version, snh_account_manager
import snhwalker_utils
import json

class TiktokAPIConverter:
        def __init__(self, dataobject):
            self.dataobject = dataobject
        pass

        def get_object_type(self):
            if "cid" in self.dataobject:
                return "tiktok_comment"
            if "uid" in self.dataobject:
                return "tiktok_user"
            if "comments" in self.dataobject:
                return "tiktok_commentlist"                

        def isUser(self):
            return "uid" in self.dataobject

        def isComment(self):
            return "cid" in self.dataobject     

        def isCommentlist(self):
            return "comments" in self.dataobject    

        def asTiktok_comment_list(self):
            return self.dataobject["comments"]

        def asSNHUserdata(self):
            if self.isUser():
                userdata = snhwalker.CreateDictSNUserData()        
                userdata['UserName'] = self.dataobject["nickname"]
                
                userdata['UserID'] = self.dataobject["unique_id"]
                userdata['UserIDNumber'] = self.dataobject["uid"]

                if "avatar_thumb" in self.dataobject:
                    if "url_list" in self.dataobject["avatar_thumb"]:
                        if len(self.dataobject["avatar_thumb"]["url_list"]) > 0:
                            userdata['UserProfilePictureURL'] = self.dataobject["avatar_thumb"]["url_list"][0]

                userdata['ProfileType'] = 0   
                userdata['UserURL'] = GetURL_Profile(userdata['UserID'])
                return userdata    
            else:
                return None    

        def asSNHCommentdata(self, isAnswer, postingID, rootCommentId = 0):
            if self.isComment():
                tempComment = snhwalker_utils.snh_model_manager.CreateDictSNCommentdata()
                
                tempComment['User'] = TiktokAPIConverter(self.dataobject["user"]).asSNHUserdata()
                if tempComment['User'] is None:
                    tempComment['User'] = snhwalker.CreateDictSNUserData()  


                tempComment['Timestamp'] = self.dataobject["create_time"]
                tempComment['Content'] = self.dataobject["text"]
                
                tempComment['__tiktokid__'] = self.dataobject["cid"]
                tempComment['__digg_count__'] = self.dataobject["digg_count"]
                tempComment['PostingID'] = postingID
                tempComment['Answer'] = isAnswer
                tempComment['AnswerID'] = rootCommentId
                tempComment['CommentID'] = snhwalker_utils.snh_model_manager.GetUniqueCommentID(tempComment)
                return tempComment    
            else:
                return None    
             