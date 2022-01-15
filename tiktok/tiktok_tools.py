#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_tools.py
@Time    :   2022/01/06 18:24:03
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2021, Freezingdata GmbH
@Desc    :   None
'''

#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   module_tools.py
@Time    :   2021/11/06 11:32:53
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2021, Freezingdata GmbH
@Desc    :   None
'''

import snhwalker_utils
from snhwalker_utils import snhwalker
import re
import json
import time

""" The module contains the following functions:

    - getRegex(text, expression, no)
    - checkJson(myjson)
    - getJsonElement(inputJsonElement)
    - scrollDOM(DOMItem)
    - openURLbyClick(url):
    
"""


def split_into_lines_return_filter(a_string, filter):
    lines = a_string.splitlines()
    for line in lines:
        if filter in line:
            return line    
    return ''

def getRegex(text, expression, no):
    # Extrahiert einen Teilstring aus einem String mit einem
    # Regulaeren Ausdruck
    try:
        return re.search(expression, text).group(no)
    except AttributeError:
        return ''


def checkJson(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def getJsonElement(inputJsonElement):
    try:
        return inputJsonElement
    except:
        return ''


def scrollDOM(DOMItem):
    # scrollen in einem bestimmten DOM Bereich
    ScrollTime = time.time()
    ScrollPointY = snhwalker_utils.snh_browser.GetJavascriptInteger(DOMItem + '.scrollTop')
    while (time.time() - ScrollTime) < 2:
        snhwalker_utils.snh_browser.WaitMS(100)
        snhwalker_utils.snh_browser.ExecuteJavascript(DOMItem + '.scrollTop +=10000')
        ScrollPoint1Y = snhwalker_utils.snh_browser.GetJavascriptInteger(DOMItem + '.scrollTop')
        if (ScrollPoint1Y > ScrollPointY):
            ScrollTime = time.time()
            ScrollPointY = ScrollPoint1Y


def openURLbyClick(url):
    js = """
    function openURL(gotoUrl) {
      var element = document.createElement('a');
      element.setAttribute('href', gotoUrl);
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }
    openURL('""" + url + """')
    """
    snhwalker_utils.snh_browser.ExecuteJavascript(js)