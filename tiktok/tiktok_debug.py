#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   tiktok_debug.py
@Time    :   2022/01/06 18:11:43
@Author  :   Benno Krause 
@Contact :   bk@freezingdata.de
@License :   (C)Copyright 2020-2021, Freezingdata GmbH
@Desc    :   None
'''

import os

debugConfig = {
    "enableDebugFileOutput"       : True,
    "enableDebugLog"              : True,
    "debugFolderLocation"         : "c:\\SNH-Temp\\tiktok\\",
    "debugLevelThreshold"         : 0  
}

def initDebug(task_item):
    global debugConfig
    if "Debug" in task_item:
        debugConfig = task_item["Debug"]


def debugPrint(*text):
    if debugConfig["enableDebugLog"] is True:
        data = tuple(str(x) for x in text)
        print(" | ".join(data))
        if debugConfig["enableDebugFileOutput"] is True:
            if not os.path.exists(debugConfig["debugFolderLocation"]):
                os.makedirs(debugConfig["debugFolderLocation"])
            debugFile = open(debugConfig["debugFolderLocation"] + "tiktok.log", 'a', encoding="utf-8")
            debugFile.write(" | ".join(data))
            debugFile.close()

def debugWrite(filepath, content):
    if debugConfig["enableDebugFileOutput"] is True:
        if not os.path.exists(debugConfig["debugFolderLocation"]):
            os.makedirs(debugConfig["debugFolderLocation"])
        contentfile = open(debugConfig["debugFolderLocation"] + filepath, 'w', encoding="utf-8")
        contentfile.write(content)
        contentfile.write("\n")
        contentfile.close()
        debugPrint("Write Debug File in " + debugConfig["debugFolderLocation"] + filepath)
