from snhwalker_utils import snhwalker, snh_major_version, snh_account_manager
import snhwalker_utils


from tiktok.tiktok_debug import *
from tiktok.tiktok_urls import *
from tiktok.tiktok_config import modul_config
from tiktok.tiktok_profile_collector import TiktokProfileCollector
from tiktok.tiktok_timeline_collector import TiktokTimelineCollector

def getPluginInfo():
    return {
        'name': 'TikTok',
        'url': 'https://www.tiktok.com/',
        'copyright': 'Freezingdata GmbH',
        'functions': {
            'profile': True,
            'groups': False,
            'details': False,
            'stories': False,
            'videos': True,
            'friends': False,
            'timeline': True,
            'timelinereactions': False, 
            'timelinecomments': True,
            'media': False, 
            'mediareactions': False,
            'mediacomments': False
        }
    }

def snh_GetUrl(profile, urlType):
    debugPrint('snh_GetUrl: ' + urlType)
    if urlType == "OwnProfile":
        result = GetURL_OwnProfile(profile["UserID"], profile["UserIDNumber"])
    elif urlType == "Timeline":
        result = GetURL_Profile(profile["UserID"], profile["UserIDNumber"])
    elif urlType == "Profile":
        result = GetURL_Profile(profile["UserID"], profile["UserIDNumber"])
    elif urlType == "Friends":
        result = GetURL_Friends(profile["UserID"], profile["UserIDNumber"])
    elif urlType == "Group":
        result = ''
    return result

def snh_Save(taskItem):
    initDebug(taskItem)
    debugPrint('[START] snh_Save ' + taskItem["TargetType"])
    if taskItem["TargetType"] == "Profile":
        TiktokProfileCollector().save_profile(taskItem["TargetURL"])
    elif taskItem["TargetType"] == "Timeline":
        TiktokTimelineCollector(taskItem["Targetprofile"], taskItem["Config"]).run()
        pass
    elif taskItem["TargetType"] == "ProfileDetails":
        pass
    elif taskItem["TargetType"] == "Media":
        pass
    elif taskItem["TargetType"] == "Friends":
        pass

def HandleProfile():
    TiktokProfileCollector().handle_profile()

def GetProfileStatus():
    # Not used
    return True

def GetLoginStatus():
    # Not used
    return True

def doLogin(userid, password):
    # Not used
    return True

def CurrentWebPageIsUser():
    # Not used
    return TiktokProfileCollector().current_is_user()

def CurrentWebPageIsPage():
    # Not used
    return TiktokProfileCollector().current_is_page()

def CurrentWebPageIsGroup():
    # Not used
    return TiktokProfileCollector().current_is_group()

def DisableUseraccountData():
    pass

def EnableUseraccountData():
    pass  

