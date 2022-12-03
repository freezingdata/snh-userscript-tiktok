from email import header


#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_config.py
@Time    :   2022/03/19
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2022, Freezingdata GmbH
@Desc    :   None
'''

modul_config = {
    # simple_timeline_collection
    # Type: boolean
    # If its set to True, just the videos will be collected.
    # To collect comments, or save the original posting screenshot, it has set to False
    "simple_timeline_collection": False,

    # limit_root_comments
    # Type: boolean
    # True if the count of collected 1st level comments should be resticted
    "limit_root_comments": True,

    # limit_root_comment_count
    # Type: integer
    # Max count of 1st level comments, which can be collected,
    "limit_root_comment_count": 100,

    # load_comment_answers
    # Type: boolean
    # Indicates whether comment answers should be collected or not
    "load_comment_answers": True,

    # limit_comment_answers
    # Type: boolean
    # If is is set True, answers are just collected, if it's root comment is inside the limit_comment_answers_count limit
    "limit_comment_answers": True,    

    # limit_comment_answers_count
    # Type: integer
    # Max count of 1st level comments, which are considered for checking of answers
    "limit_comment_answers_count": 100,
}