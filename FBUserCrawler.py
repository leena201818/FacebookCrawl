# -*- coding: utf-8 -*-
import logging
import time, datetime
import random
import os
# import os.
import json
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from  selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import ProxyType

from loghelper.loghelper import logHelper
from FBLogin import isLogin, login_by_up, login_by_cookie, login_by_up_userpage, login_by_up_Homepage
from utility import OurFBAccount
from utility import FBHelper, TimeHelper, FBBaseUser, Analyzer
import FBUserHelper


# class FBUserCrawler():
#     def __init__(self):
#         self.fbuserhelper = FBUserHelper.FBUserHelper()

# 初始化，返回bowser，和是否登录成功
def initCrawler(init_url, fbAccount):
    browser = ChangeConfigInProfile()
    
    FBHelper.openUrl_exit(browser, init_url, 10)
    # browser.get(init_url)
    logHelper.getLogger().info("open url:" + init_url)

    time.sleep(random.randint(1, 6))
    # FBHelper.save2Html(browser, "000000000000", "")
    loginFlag = isLogin(browser, fbAccount.fbid)
    iCount = 0
    while not loginFlag:
        iCount += 1
        logHelper.getLogger().info("not login,try to login ")
        #  先用cookie登录
        if os.path.exists('FBCookie.txt'):
            loginFlag = login_by_cookie(browser, 'FBCookie.txt', fbAccount.fbid)
        if not loginFlag:
            loginFlag = login_by_up_Homepage(browser, fbAccount, 'FBCookie.txt')

        if iCount > 11:
            logHelper.getLogger().info("try to login for " + str(iCount) + " times, all failed, please check!")
            break;
    # FBHelper.save2Html(browser, "000000000000")
    return browser, loginFlag


def ChangeConfigInProfile():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("dom.webnotifications.enabled", False)
    profile.set_preference("dom.push.enabled", False)
    profile.update_preferences()
    return webdriver.Firefox(firefox_profile=profile, timeout = 20)


def crawleInfo(browser, fbUser, fbAccount):
    # datetime.datetime.utcfromtimestamp(timeStamp)
    base_url = "https://www.facebook.com/"
    start_url = base_url + fbUser.fbid
    logHelper.getLogger().info("Try to crawle the info of " + fbUser.fbid)
    # isOpened = FBHelper.openUrl(browser, start_url, 10) #yyyy
    checkResult = FBHelper.checkAccount(browser,start_url,5)
    logHelper.getLogger().debug(checkResult)

    if checkResult == 'NetError':
        logHelper.getLogger().info("Please check your network status!")
        logHelper.getLogger().info("Task of " + fbUser.fbid + " is failed!")
        return 0
    elif checkResult == 'OtherError':
        logHelper.getLogger().info("unknown error!")
        logHelper.getLogger().info("Task of " + fbUser.fbid + " is failed!")
        return 0
    elif checkResult == 'OutAccountForbidden':
        logHelper.getLogger().info("Please change your account!")
        logHelper.getLogger().info("Task of " + fbUser.fbid + " is failed!")
        return 2
    elif checkResult == 'TargetFBIDInValid':
        logHelper.getLogger().info("the target fbid {} account is invalid!".format(fbUser.fbid))
        logHelper.getLogger().info("Task of " + fbUser.fbid + " is failed!")
        return 3

    time.sleep(random.randint(1, 4))
    RDList = [1, 2, 3, 4, 5]
    random.shuffle(RDList)
    rtnValue = 0

    for idx in RDList:
        if idx == 1:
            pass
            # 失败返回-1
            # rst = crawleTimelines(browser, fbUser, False)
            # rst = crawleTimelines_batch(browser, fbUser, False)
            # if rst == -1:
            #     logHelper.getLogger().info("Failed to crawle the timeline info of %s" % fbUser.fbid)
            # elif rst >=0:
            #     logHelper.getLogger().info("Crawle all timelime of %s completed!" % fbUser.fbid)
            # else:
            #     logHelper.getLogger().info("When Crawle the timelimes of %s, something unkown occured!" % fbUser.fbid)
        elif idx == 2:
            # pass
            crawleAbout(browser, fbUser)
        elif idx == 3:
            # pass
            crawleFriends(browser, fbUser, False)
        elif idx == 4:
            pass
            # crawleImage(browser, fbUser)
        else:
            tab_nav = FBHelper.find_element(browser, \
                                            '''//div[@id="fbTimelineHeadline"]/div[@class="_70k"]/
       ul[@data-referrer="timeline_light_nav_top"]/li/a''', \
                                            "Nav TAB is NOT found!", \
                                            "find_elements_by_xpath")
            if tab_nav is None:
                continue
            else:
                for navItem in tab_nav:
                    itemName = navItem.get_attribute("data-tab-key")
                    if itemName == "friends":
                        continue
                    elif itemName == "timeline":
                        continue
                    elif itemName == "about":
                        continue
                    else:
                        FBHelper.eleClick(navItem)
                        # try:
                        #     navItem.click()
                        # except Exception as e:
                        #     logHelper.getLogger().error(e)
                        #     logHelper.getLogger().error("please check status of your network!")

                        # time.sleep(2)
                        time.sleep(random.randint(3, 5))  # yyyy
                        break;
        time.sleep(random.randint(3, 8))  # yyyy
    print("Task {} is completed, go to Sleep".format(fbUser.fbid))  # yyyy
    time.sleep(random.randint(5, 10))  # yyyy
    return 1


def crawleFriends(browser, fbUser, deepFlag=False):
    logHelper.getLogger().info("Try to crawle the friends info of " + fbUser.fbid)
    #  ul 的ID 有时会变
    # tab_Frnds1Level = FBHelper.find_element(browser,'//ul[@id = "u_0_m"]/li/a[@data-tab-key="friends"]',\
    #                                         "TAB friend is NOT found!")

    tab_Frnds1Level = FBHelper.find_element(browser, '''//div[@id="fbTimelineHeadline"]/div[@class="_70k"]/
    ul[@data-referrer="timeline_light_nav_top"]/li/a[@data-tab-key="friends"]''', \
                                            "TAB friend is NOT found!")

    if tab_Frnds1Level is None:
        return

    # time.sleep(random.randint(1, 5))
    if not FBHelper.eleClick(tab_Frnds1Level):
        logHelper.getLogger().warning(
            "Stop to crawle the friends info of %s because of status of your network!" % fbUser.fbid)
        return
    # tab_Frnds1Level.click()
    # time.sleep(random.randint(1, 5))

    FBHelper.save2Html(browser, fbUser.fbid, "friends")
    # 个人主页朋友列表页面，朋友分类导航
    # class 有部分为 _3dc lfloat _ohe _5brz _5bry   有的为_3dc lfloat _ohe _5brz
    tab_Frnds2Level = FBHelper.find_element(browser, '''//div[@id="pagelet_timeline_medley_friends"]
        //div[contains(@class,"_3dc") and contains(@class,"lfloat") and contains(@class,"_ohe") and 
        contains(@class,"_5brz") and @role="tablist"]''', \
                                            "THE NAV OF Friends BLOCK is NOT found!")
    if tab_Frnds2Level is None:
        return

    # 页面一切正常
    RDList = getShuffledList(4)
    for iType in RDList:
        if iType == 1:  # all Friends
            # pass
            crawleFriends_All(browser, fbUser)
        elif iType == 2:  # Following
            if deepFlag:
                # pass
                crawleFriends_Following(browser, fbUser)
        elif iType == 3:  # Current City
            if deepFlag:
                crawleFriends_CurrentCity(browser, fbUser)
        else:  ### 还有多个朋友块导航，加干扰
            navItem = FBHelper.find_element(tab_Frnds2Level, './a', \
                                            "THE NAV OF Friends Kind has no item!", \
                                            'find_elements_by_xpath')
            if navItem is None:
                continue

            tmpList = getShuffledList(len(navItem))
            for tmpI in tmpList:
                if navItem[tmpI - 1].get_attribute('name') == 'All Friends' \
                        or navItem[tmpI - 1].text == 'Following' \
                        or navItem[tmpI - 1].text == 'Current City':
                    continue
                else:
                    # navItem[tmpI-1].click()
                    if not FBHelper.eleClick(navItem[tmpI - 1]):
                        logHelper.getLogger().warning(
                            "Stop to MO FANG action because of status of your network!")
                        return
                    logHelper.getLogger().info('Random rest for a few seconds')
                    # time.sleep(random.randint(2, 6))  # 模拟浏览随机秒数
                    time.sleep(random.randint(6, 12))  # 模拟浏览随机秒数#yyyy
                    break
        time.sleep(random.randint(4, 10))  # yyyy


def crawleFriends_All(browser, fbUser):
    # 个人主页朋友列表页面，朋友分类导航
    # class 有部分为 _3dc lfloat _ohe _5brz _5bry   有的为_3dc lfloat _ohe _5brz
    frndKindNav = FBHelper.find_element(browser, '''//div[@id="pagelet_timeline_medley_friends"]
        //div[contains(@class,"_3dc") and contains(@class,"lfloat") and contains(@class,"_ohe") and 
        contains(@class,"_5brz") and @role="tablist"]''', \
                                        "THE NAV OF Friends BLOCK is NOT found!")
    if frndKindNav is None:
        return -1

    AllFrndItem = FBHelper.find_element(frndKindNav, r'./a[@name="All friends"]', \
                                        "All friend ITEM is not found!")
    if AllFrndItem is None:
        AllFrndItem = FBHelper.find_element(frndKindNav, r'./a[@name="All Friends"]', \
                                        "All Friend ITEM is not found!")
        if AllFrndItem is None:
            return -1

    # 拖至页面底部
    # time.sleep(random.randint(1, 4))  # 随机休息几秒
    time.sleep(random.randint(4, 10))  # 随机休息几秒#yyyy
    # AllFrndItem.click()
    if not FBHelper.eleClick(AllFrndItem):
        logHelper.getLogger().warning(
            "Stop to crawle ALL friends info of %s because of status of your network!" % fbUser.fbid)
        return -1

    logHelper.getLogger().info("Now we are in All Friends page!")
    scroll2Bottom(browser)

    FBHelper.save2Html(browser, fbUser.fbid, "friends_all")

    frndList = FBHelper.find_element(browser, \
                                     r'''//div[@class="uiProfileBlockContent"]/div[@class="_6a"]
                                     /div[contains(@class,"_6a") and contains(@class,"_6b")]
                                     /div[contains(@class,"fsl") and contains(@class,"fwb") and contains(@class,"fcb")]/..''', \
                                     "Friends in All Friend kinds(element) is not found!", \
                                     'find_elements_by_xpath')
    if frndList is None:
        return -1

    sCount = 0
    #  爬取的数据存放地
    sData = {}
    sData['fbida'] = fbUser.fbid
    sData['namea'] = fbUser.name
    sData['deep'] = fbUser.deep + 1
    sData['relationtype'] = "friend"
    if len(frndList) > 0:
        logHelper.getLogger().info(str(len(frndList)) + ' friends are found')
        logHelper.getLogger().info('Begin to crawle detail information!')
        # f = open("crawledInfo" + os.sep + fbid + '_friends.txt', 'w', encoding='utf-8')

        fbuserhelper = FBUserHelper.FBUserHelper()
        lstsData = []

        for i, tmpItem in enumerate(frndList):
            sData['Description'] = ""
            sData['fbidb'] = ""
            sData['nameb'] = ""
            # sData['homepage']       = "" #"'www.facebook.com/{0}'.format(fbidb)
            logHelper.getLogger().info(str(i + 1) + 'th friend info:')
            idNode = FBHelper.find_element(tmpItem,
                                           r'./div[contains(@class,"fsl") and contains(@class,"fwb") and contains(@class,"fcb")]/a', \
                                           'Crawle ' + str(i + 1) + "th friend FBID AND NAME failed!")
            #  拿不到id,不进行任何操作 且 朋友名称不为空
            if idNode is not None and idNode.text is not None \
                    and idNode.text.replace("\n", "").replace(" ", "") != "":
                try:
                    sData['nameb'] = idNode.text
                    #  data-hovercard = "/ajax/hovercard/user.php?id=100009331436324&extragetparams=%7B%22hc_location%22%3A%22friends_tab%22%7D"
                    sData['fbidb'] = idNode.get_attribute('data-hovercard').split("?")[-1].split("&")[0].split("=")[-1]
                    sData['homepage'] = idNode.get_attribute('href').split("?")[0]
                    if sData['homepage'].find('/profile.php') >= 0:
                        sData['homepage'] = 'www.facebook.com/%s' % sData['fbidb']
                    logHelper.getLogger().info("fbid:" + sData['fbidb'])
                    descNode = FBHelper.find_element(tmpItem, r'ul[@class="uiList _4kg"]/li', \
                                                     'Crawle ' + str(i + 1) + "th friend DESC failed!", \
                                                     "find_elements_by_xpath")
                    # descStr = ""
                    if descNode is not None:
                        #  描述可能有多条
                        for j, descItem in enumerate(descNode):
                            sData['Description'] += descItem.text + os.linesep

                    sData['priority'] = Analyzer.computerPriority(fbUser, sData['Description'], sData['deep'])
                    # if sData['Description'].find
                    # saveFriends(fbuserhelper, sData)
                    lstsData.append(sData.copy())
                    # 成功后计数
                    sCount += 1
                except Exception as e:
                    logHelper.getLogger().error(e)
                    logHelper.getLogger()("crawle %ith friends of %s failed" % (i + 1, fbUser.fbid))
        saveFriendsBatch(fbuserhelper, lstsData)
    else:
        logHelper.getLogger().warning("Friends in All Friend kinds(Friends) is not found!")

    logHelper.getLogger().info("Successfully crawled %s Friends of %s" % (sCount, fbUser.fbid))
    return sCount


# 保存朋友同时保存关系
def saveFriendsBatch(fbuserhelper, lstsData):
    # import json
    # with open(r'lstspdata.txt','w') as f:
    #     json.dump(lstsData,f)

    # 保存朋友# 入库friends
    lstDicResult = []
    lstDicResult2 = []
    for pDict in lstsData:
        dicResult1 = {'fbid': pDict['fbidb'], 'name': pDict['nameb'], 'homepage': pDict['homepage'], \
                      'priority': pDict['priority'], 'Description': pDict['Description'], 'deep': pDict['deep']}
        lstDicResult.append(dicResult1)

        dicResult2 = {'fbida': pDict['fbida'], "namea": pDict['namea'], 'fbidb': pDict['fbidb'],
                      "nameb": pDict['nameb'], 'relationtype': pDict['relationtype']}
        lstDicResult2.append(dicResult2)

    fbuserhelper.Save_tb_user_friends_batch(lstDicResult)
    # 入库ralationship
    fbuserhelper.Save_tb_user_relationship_batch(lstDicResult2)

#cancel
def saveFriends(fbuserhelper, pDict):
    if len(pDict['nameb']) > 80:  # 名字截断 最大80字符
        pDict['nameb'] = pDict['nameb'][0:80]
    # 保存朋友# 入库friends
    # homePage = 'www.facebook.com/%s' % pDict['fbidb']
    dicResult1 = {'fbid': pDict['fbidb'], 'name': pDict['nameb'], 'homepage': pDict['homepage'], \
                  'priority': pDict['priority'], 'Description': pDict['Description'], 'deep': pDict['deep']}
    fbuserhelper.Save_tb_user_friends(dicResult1)
    # 入库ralationship
    # 保存关系，参数采用字典方式，注意检查对应！
    dicResult2 = {'fbida': pDict['fbida'], "namea": pDict['namea'], 'fbidb': pDict['fbidb'],
                  "nameb": pDict['nameb'], 'relationtype': pDict['relationtype']}
    fbuserhelper.Save_tb_user_relationship(dicResult2)


def crawleFriends_CurrentCity(browser, fbUser):
    # 个人主页朋友列表页面，朋友分类导航
    # class 有部分为 _3dc lfloat _ohe _5brz _5bry   有的为_3dc lfloat _ohe _5brz
    frndKindNav = FBHelper.find_element(browser, '''//div[@id="pagelet_timeline_medley_friends"]
        //div[contains(@class,"_3dc") and contains(@class,"lfloat") and contains(@class,"_ohe") and 
        contains(@class,"_5brz") and @role="tablist"]''', \
                                        "THE NAV OF Friends BLOCK is NOT found!")
    if frndKindNav is None:
        return -1

    CurrentCityItem = FBHelper.find_element(frndKindNav, r'./a[@name="Current City"]', \
                                            "CurrentCity ITEM is not found!")
    if CurrentCityItem is None:
        return -1

    # 拖至页面底部
    # time.sleep(random.randint(1, 4))  # 随机休息几秒
    time.sleep(random.randint(4, 10))  # 随机休息几秒#yyyy
    # CurrentCityItem.click()
    if not FBHelper.eleClick(CurrentCityItem):
        logHelper.getLogger().warning(
            "Stop to crawle the current city friends info of %s because of status of your network!" % fbUser.fbid)
        return -1

    logHelper.getLogger().info("Now we are in Current City friends page!")
    scroll2Bottom(browser)

    FBHelper.save2Html(browser, fbUser.fbid, "friends_currentCity")

    frndList = FBHelper.find_element(browser, \
                                     r'''//div[@class="uiProfileBlockContent"]/div[@class="_6a"]
                                     /div[contains(@class,"_6a") and contains(@class,"_6b")]
                                     /div[contains(@class,"fsl") and contains(@class,"fwb") and contains(@class,"fcb")]/..''', \
                                     "Friends in Current City kinds(element) is not found!", \
                                     'find_elements_by_xpath')
    if frndList is None:
        return -1

    sCount = 0
    #  爬取的数据存放地
    sData = {}
    sData['fbida'] = fbUser.fbid
    sData['namea'] = fbUser.name
    # sData['priority']       = fbUser.priority - 1
    sData['deep'] = fbUser.deep + 1
    sData['relationtype'] = "friend.CurrentCity"

    if len(frndList) > 0:
        fbuserhelper = FBUserHelper.FBUserHelper()
        logHelper.getLogger().info(str(len(frndList)) + ' friends are found')
        logHelper.getLogger().info('Begin to crawle detail information!')

        lstsData = []
        for i, tmpItem in enumerate(frndList):
            sData['fbidb'] = ""
            sData['nameb'] = ""
            sData['Description'] = ""
            logHelper.getLogger().info(str(i + 1) + 'th friend info :')
            idNode = FBHelper.find_element(tmpItem,
                                           r'./div[contains(@class,"fsl") and contains(@class,"fwb") and contains(@class,"fcb")]/a', \
                                           'Crawle ' + str(i + 1) + "th friend FBID AND NAME failed!")
            # 无名字的不取
            if idNode is not None and idNode.text is not None \
                    and idNode.text.replace("\n", "").replace(" ", "") != "":
                try:
                    sData['nameb'] = idNode.text
                    #  data-hovercard = "/ajax/hovercard/user.php?id=100009331436324&extragetparams=%7B%22hc_location%22%3A%22friends_tab%22%7D"
                    sData['fbidb'] = idNode.get_attribute('data-hovercard').split("?")[-1].split("&")[0].split("=")[-1]
                    sData['homepage'] = idNode.get_attribute('href').split("?")[0]
                    if sData['homepage'].find('/profile.php') >= 0:
                        sData['homepage'] = 'www.facebook.com/%s' % sData['fbidb']
                    logHelper.getLogger().info("fbid:" + sData['fbidb'])
                    descNode = FBHelper.find_element(tmpItem, r'ul[@class="uiList _4kg"]/li', \
                                                     'Crawle ' + str(i + 1) + "th friend DESC failed!", \
                                                     'find_elements_by_xpath')
                    sData['Description'] = ""
                    if descNode is not None:
                        #  描述可能有多条
                        for j, descItem in enumerate(descNode):
                            # logHelper.getLogger().info(str(i+1) + "th friends " + str(j+1) + "th desc: " + tmpItem.text)
                            sData['Description'] += descItem.text + " "

                    sData['priority'] = Analyzer.computerPriority(fbUser, sData['Description'], sData['deep'])
                    # 保存朋友
                    # saveFriends(fbuserhelper, sData)

                    lstsData.append(sData.copy())
                    sCount += 1
                except Exception as e:
                    logHelper.getLogger().error(e)
                    logHelper.getLogger().warning("crawle %ith CurrentCity friends of %s failed" % (i + 1, fbUser.fbid))

        saveFriendsBatch(fbuserhelper, lstsData)
    else:
        logHelper.getLogger().warning("Friends in CurrentCity kinds(Friends) is not found!")

    logHelper.getLogger().info("Successfully crawled %s CurrentCity Friends of %s" % (sCount, fbUser.fbid))
    return sCount


def crawleFriends_Following(browser, fbUser):
    # 个人主页朋友列表页面，朋友分类导航
    # class 有部分为 _3dc lfloat _ohe _5brz _5bry   有的为_3dc lfloat _ohe _5brz
    frndKindNav = FBHelper.find_element(browser, '''//div[@id="pagelet_timeline_medley_friends"]
        //div[contains(@class,"_3dc") and contains(@class,"lfloat") and contains(@class,"_ohe") and 
        contains(@class,"_5brz") and @role="tablist"]''', \
                                        "THE NAV OF Friends BLOCK is NOT found!")
    if frndKindNav is None:
        return -1

    FollowingFrndItem = FBHelper.find_element(frndKindNav, r'./a[@name="Following"]', \
                                              "Following ITEM is not found!")
    if FollowingFrndItem is None:
        return -1

    # 拖至页面底部
    # time.sleep(random.randint(1, 4))  # 随机休息几秒
    time.sleep(random.randint(4, 10))  # 随机休息几秒#yyyy
    # FollowingFrndItem.click()
    if not FBHelper.eleClick(FollowingFrndItem):
        logHelper.getLogger().warning(
            "Stop to crawle the following friends info of %s because of status of your network!" % fbUser.fbid)
        return -1

    logHelper.getLogger().info("Now we are in Following friends page!")
    scroll2Bottom(browser)

    FBHelper.save2Html(browser, fbUser.fbid, 'friends_following')

    # frndList = browser.find_elements_by_xpath(r'//div[@class="_42ef"]/div[@class="_6a"]/div[@class="_6a _6b"]')
    # 通过子节点定位
    frndList = FBHelper.find_element(browser, \
                                     # r'//div[@class="_42ef"]/div[@class="_6a"]/div[contains(@class,"_6a") and contains(@class,"_6b")]',\
                                     '''//div[@class="_42ef"]/div[@class="_6a"]
                                     /div[contains(@class,"_6a") and contains(@class,"_6b")]
                                     /div/span[contains(@class,"fsl") and contains(@class,"fwb") and contains(@class,"fcb")]/../..''',
                                     "Friends in Following kinds(element) is not found!",
                                     'find_elements_by_xpath')
    if frndList is None:
        return -1

    sCount = 0
    #  爬取的数据存放地
    sData = {}
    sData['fbida'] = fbUser.fbid
    sData['namea'] = fbUser.name
    # sData['priority']       = fbUser.priority - 1
    sData['deep'] = fbUser.deep + 1
    sData['relationtype'] = "friend.Following"
    if len(frndList) > 0:
        fbuserhelper = FBUserHelper.FBUserHelper()
        logHelper.getLogger().info(str(len(frndList)) + ' friends are found')
        logHelper.getLogger().info('Begin to crawle detail information!')
        # f = open("crawledInfo" + os.sep + fbid + '_following.txt', 'w', encoding='utf-8')

        lstsData = []
        for i, tmpItem in enumerate(frndList):
            sData['fbidb'] = ""
            sData['nameb'] = ""
            sData['Description'] = ""
            logHelper.getLogger().info(str(i + 1) + 'th friend info:')
            idNode = FBHelper.find_element(tmpItem,
                                           r'''./div/span[contains(@class,"fsl") and 
                                                    contains(@class,"fwb") and contains(@class,"fcb")]/a''', \
                                           'crawle ' + str(i + 1) + "th friend FBID and NAME failed!")

            if idNode is not None and idNode.text is not None \
                    and idNode.text.replace("\n", "").replace(" ", "") != "":
                try:
                    sData['nameb'] = idNode.text
                    # data-hovercard="/ajax/hovercard/user.php?id=100009873994637"
                    sData['fbidb'] = idNode.get_attribute('data-hovercard').split("=")[-1]
                    sData['homepage'] = idNode.get_attribute('href').split("?")[0]
                    if sData['homepage'].find('/profile.php') >= 0:
                        sData['homepage'] = 'www.facebook.com/%s' % sData['fbidb']
                    logHelper.getLogger().info("fbid:" + sData['fbidb'])
                    followersNode = FBHelper.find_element(tmpItem, r'./div/div[@class ="fsm fwn fcg"]', \
                                                          'crawle ' + str(i + 1) + "th friend followers failed!")
                    descNode = FBHelper.find_element(tmpItem, r'ul[@class="uiList _4kg"]/li', \
                                                     'Crawle ' + str(i + 1) + "th friend DESC failed!", \
                                                     "find_elements_by_xpath")
                    sData['Description'] = ""
                    if followersNode is not None:
                        followers = followersNode.text
                        followers = followers.replace("followers", "").replace(",", "")
                        sData['Description'] += "followers:" + followers + os.linesep
                        logHelper.getLogger().info("followers:" + followers)

                    if descNode is not None:
                        #  描述可能有多条
                        for j, descItem in enumerate(descNode):
                            sData['Description'] += descItem.text + os.linesep

                    sData['priority'] = Analyzer.computerPriority(fbUser, sData['Description'], sData['deep'])
                    # 保存朋友
                    # saveFriends(fbuserhelper, sData)

                    lstsData.append(sData.copy())
                    sCount += 1
                except Exception as e:
                    logHelper.getLogger().error(e)
                    logHelper.getLogger().warning("crawle %ith Fowllowing friends of %s failed" % (i + 1, fbUser.fbid))

        saveFriendsBatch(fbuserhelper, lstsData)
    else:
        logHelper.getLogger().warning("Friends in Following kinds(Friends) is not found!")

    logHelper.getLogger().info("Successfully crawled %s Fowllowing Friends of of %s" % (sCount, fbUser.fbid))
    return sCount


def getShuffledList(count):
    RDList = [i + 1 for i in range(count)]
    random.shuffle(RDList)
    return RDList


def scroll2Bottom(browser, maxCount=None):
    allBodyPre = browser.page_source
    iCount = 0
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        iCount += 1
        # time.sleep(random.randint(1, 5))
        time.sleep(random.randint(2, 5))  # yyyy
        logHelper.getLogger().info("%sth time Scroll to the bottom to fetch more information" % iCount)

        if maxCount is not None:
            if iCount > maxCount:
                break
        allBodySrolled = browser.page_source
        if len(allBodySrolled) == len(allBodyPre):
            logHelper.getLogger().info("no more information can be found!")
            break
        else:
            allBodyPre = allBodySrolled

# cancel
def crawleTimelines(browser, fbUser, deepFlag=False):
    logHelper.getLogger().info("Try to crawle the timeline info of " + fbUser.fbid)
    # tab_timeline = FBHelper.find_element(browser,\
    #                                      '//ul[@id = "u_0_m"]/li/a[@data-tab-key="timeline"]', \
    #                                      "TAB timeline is NOT found!")
    tab_timeline = FBHelper.find_element(browser, \
                                         '''//div[@id="fbTimelineHeadline"]/div[@class="_70k"]/
    ul[@data-referrer="timeline_light_nav_top"]/li/a[@data-tab-key="timeline"]''', \
                                         "TAB timeline is NOT found!")
    if tab_timeline is None:
        return -1

    # time.sleep(random.randint(2, 6))
    # tab_timeline.click()
    if not FBHelper.eleClick(tab_timeline):
        logHelper.getLogger().warning(
            "Stop to crawle the timeline info of %s because of status of your network!" % fbUser.fbid)
        return -1
    scroll2Bottom(browser, 2)
    FBHelper.save2Html(browser, fbUser.fbid, 'timeline')
    # time.sleep(random.randint(1, 4))

    # div[@class="fbUserContent _5pcr"]  还有可能为 class="_5pcr fbUserPost",_5pcr fbUserStory
    # 他往上两级 节点可以获取该timeline 的id
    eleList = FBHelper.find_element(browser, \
                                    r'''//div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent") or contains(@class,"fbUserStory"))]
                                    /../..''', \
                                    "No timeline is found!", \
                                    "find_elements_by_xpath")

    if eleList is None:
        return -1

    tCount = 0
    if len(eleList) > 0:
        fbuserhelper = FBUserHelper.FBUserHelper()
        logHelper.getLogger().info(str(len(eleList)) + ' timeline are found')
        logHelper.getLogger().info('Begin to crawle timeline detail information!')
        for i, tmpItem in enumerate(eleList):
            tCount += extractTLInfo(browser, fbUser, fbuserhelper, tmpItem, i, deepFlag=deepFlag)
        logHelper.getLogger().info('Successfully crawled %s timelines of %s' % (tCount, fbUser.fbid))

    return tCount  # 数字表示正确爬取了几条动态信息
    # else:
    #     return "0" # 字符0 表示没有找 一条动态信息

    # logHelper.getLogger().info('Successfully crawled %s timelines of %s' % (tCount, fbUser.fbid))

# 抽取单个timeline具体信息并入库
# cancel
def extractTLInfo(browser, fbUser, fbuserhelper, TLNode, i, bTimestamp=0, deepFlag=False):
    logHelper.getLogger().info(str(i + 1) + 'th timeline info: ')
    # idNode = FBHelper.find_element(tmpItem,
    #                                './parent/parent',
    #                                str(i + 1) + "th timeline's id is not found!")
    # if idNode is None:
    #     continue
    tlID = TLNode.get_attribute("id")
    # FBHelper.find_element(tmpItem,'./parent/parent',
    #                       str(i + 1) + "th timeline's id is not found!")
    #  105 friends posted on Indraveer's Timeline 没有 id为空，过滤掉
    #  只找自己发的
    if tlID is not None and tlID.strip() != "":
        logHelper.getLogger().info("timelineID:" + tlID)
        timeStamp = TLNode.get_attribute("data-time")
        if int(timeStamp) > bTimestamp:
            rIDNode = FBHelper.find_element(TLNode, \
                                            r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent"))]
                                            //div/form/input[2]''', \
                                            str(i + 1) + "th timeline's id node is not found!")
            timeNode = FBHelper.find_element(TLNode, \
                                             r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent"))]
                                             //div[contains(@class,"_1dwg") and contains(@class,"_1w_m")]
                                             //abbr[@data-utime]''', \
                                             str(i + 1) + "th timeline's post time is not found!")

            # @ class ="_5pbx userContent"
            contentNode = FBHelper.find_element(TLNode, \
                                                r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent"))]
                                                //div[contains(@class,"_1dwg") and contains(@class,"_1w_m")]
                                                //div[contains(@class,"userContent")]''', \
                                                str(i + 1) + "th timeline's has not text content!")
            #  图片  class="_3x-2"
            imgNodes = FBHelper.find_element(TLNode,
                                             r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent"))]
                                              //div[contains(@class,"_1dwg") and contains(@class,"_1w_m")]
                                              //div[contains(@class,"_3x-2")]//a//img''',
                                             str(i + 1) + "th timeline's has not images!",
                                             "find_elements_by_xpath", )
            landMarkNode = FBHelper.find_element(TLNode, \
                                                 r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent"))]
                                                  //div[contains(@class,"_1dwg") and contains(@class,"_1w_m")]
                                                  //span[contains(@class,"fwn") and contains(@class,"fcg")]/span[@class ="fcg"]/a''',
                                                 str(i + 1) + "th timeline's has no landmark")

            DZanNode = FBHelper.find_element(TLNode, \
                                             r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent"))]
                                             //form[contains(@class,"commentable_item")]
                                             //span[contains(@class,"_4arz")]/span''',
                                             str(i + 1) + "th timeline's has no DZinfo")
            rTLID = ""
            if rIDNode is not None:
                rTLID = rIDNode.get_attribute('value')
                # 有可能是这种: ID,100001993779540:764304213646031:188881761160470:725875200
                rTLID = rTLID.split(':')[0][0:48]
                logHelper.getLogger().info("timeline ID:" + rTLID)

            postTime = ""
            if timeNode is not None:
                postTime = timeNode.get_attribute('title')
                postTime = TimeHelper.getDBTimeStr(postTime)
                logHelper.getLogger().info("time:" + postTime)
                # 66733642
            content = ""
            if contentNode is not None:
                content = contentNode.text
                # logHelper.getLogger().info("content:" + content)

            imgLink = ""
            imgAlt = ""
            if imgNodes is not None and len(imgNodes) > 0:
                for j, imageItem in enumerate(imgNodes):
                    imgLink += imageItem.get_attribute("src") + ";"
                    imgAlt += imageItem.get_attribute("alt") + ";"

            landName = ""
            landMarkID = ""
            if landMarkNode is not None:
                landName = landMarkNode.text
                # 除了地点还有可能是这种# Binay Shakya added 2 new photos.
                try:
                    landMarkID = \
                        landMarkNode.get_attribute('data-hovercard').split("?")[-1].split("&")[0].split("=")[-1]
                except Exception as e:
                    logHelper.getLogger().warning(e)
                    logHelper.getLogger().info("the element in that lacation is not landmark but others!")

            DZCount = 0
            if DZanNode is not None:
                try:
                    DZCount = DZanNode.text.replace(",", "").replace(".", "").lower().strip()
                    if DZCount != "":
                        if DZCount[-1] == 'k':
                            DZCount = DZCount[0:-1] + "000"
                        elif DZCount[-1] == 'm':
                            DZCount = DZCount[0:-1] + "000000"
                        DZCount = int(DZCount)
                        logHelper.getLogger().info("This timelime of %s has %s DZanCount!" % (fbUser.fbid, DZCount))
                    else:
                        DZCount = 0
                except Exception as e:
                    DZCount = 0
                    logHelper.getLogger().warning(e)
                    logHelper.getLogger().info("Failed to crawle the DZCount of this  timeline of %s!" \
                                               % fbUser.fbid)
            # 保存timelime
            dicResult = {'TimelineFBID': rTLID, 'postUserFBID': fbUser.fbid, 'postUserName': fbUser.name, \
                         'postTime': postTime, 'content': content, 'picturesURLs': imgLink, 'picturesAlts': imgAlt, \
                         'DZanCount': int(DZCount), 'landMarkID': landMarkID, \
                         'landMarkName': landName, 'timestamp': int(timeStamp)}
            fbuserhelper.Save_tb_user_timeline(dicResult)

            # 深度采集，获取点赞人数，更细节的话可以获取 like  love wow等人数
            if deepFlag and DZanNode is not None:
                if FBHelper.eleClick(DZanNode):
                    browser.switch_to_alert()
                    # firstDZPeopleWndEle = FBHelper.find_element(browser,'''//div[contains(@class,"_4-i2") and contains(@class,"_50f4")]
                    #                                      //div[contains(@class,"uiScrollableArea")]
                    #                                      //div[contains(@class,"uiScrollableAreaBody")]
                    #                                      //ul[contains(@class,"uiList") and contains(@class,"_4kg")]
                    #                                      /li[contains(@class,"_5i_q")]''',
                    #                             'alertWndEle can not be found!')
                    #
                    # if firstDZPeopleWndEle is not None:
                    #     ActionChains(browser).move_to_element(firstDZPeopleWndEle).perform()
                    while True:
                        # scroll2Bottom(browser)
                        seeMoreNode = FBHelper.find_element(browser,
                                                            '''//div[contains(@class,"_4-i2") and contains(@class,"_50f4")]
                                                            //div[contains(@class,"uiScrollableArea")]
                                                            //div[contains(@class,"uiScrollableAreaBody")]
                                                            //div[contains(@class,"uiMorePager")]
                                                            //a[contains(text(), "See More")]''',
                                                            "the See More button can not be found!")
                        # seeMoreNode = FBHelper.find_element(browser,
                        #                         '''//a[contains(text(), "See More")]''',
                        #                         "the See More button can not be found!")
                        if seeMoreNode is None:
                            break
                        else:
                            FBHelper.eleClick(seeMoreNode)
                            # time.sleep(1)
                            time.sleep(3)  # yyyy
                    DZanList = FBHelper.find_element(browser,
                                                     '''//div[contains(@class,"_4-i2") and contains(@class,"_50f4")]
                                                         //div[contains(@class,"uiScrollableArea")]
                                                         //div[contains(@class,"uiScrollableAreaBody")]
                                                         //ul[contains(@class,"uiList") and contains(@class,"_4kg")]
                                                         /li[contains(@class,"_5i_q")]''',
                                                     "the DZan List can not be found!",
                                                     "find_elements_by_xpath")
                    if DZanList is not None and len(DZanList) > 0:
                        if len(DZanList) != DZCount:
                            logHelper.getLogger().warning(
                                "the number of DZan peoples is unequal the tatal Number!")
                        dicResult = {'fbida': rTLID, "namea": fbUser.name, 'relationtype': "Timeline.LIKE"}
                        for j, pItem in enumerate(DZanList):
                            logHelper.getLogger().info("get %sth DZan people info." % str(j + 1))
                            curPeople = FBHelper.find_element(pItem,
                                                              '''.//div[contains(@class,"_6a") and contains(@class,"_6b")]
                                                              //div[contains(@class,"fsl") and contains(@class,"fwb") and contains(@class,"fcb")]
                                                              //a''',
                                                              "the %sth DZan people can not be found!" % j)
                            # data - hovercard = "/ajax/hovercard/user.php?id=100002593093964&extragetparams=%7B%22hc_location%22%3A%22profile_browser%22%7D"
                            try:
                                DZfbid = curPeople.get_attribute("data-hovercard").split("?")[-1] \
                                    .split("&")[0].split("=")[-1]
                                if DZfbid.strip() != "" and curPeople.text.strip() != "":
                                    dicResult['fbidb'] = DZfbid
                                    dicResult['nameb'] = curPeople.text.strip()
                                    fbuserhelper.Save_tb_user_relationship(dicResult)
                            except Exception as e:
                                logHelper.getLogger().error(e)
                                logHelper.getLogger().warning("Failed to extract %sth DZan people info!" % j)

                    # 关闭点赞细节窗口
                    # browser.close()
                    #  role="button" href="#" title="Close"  Close
                    closeNode = FBHelper.find_element(browser,
                                                      '''//div[contains(@class,"_4-i2") and contains(@class,"_50f4")]
                                                      //a[contains(text(), "Close")]''',
                                                      "Close button can not be found!")

                    if closeNode is not None:
                        FBHelper.eleClick(closeNode)
                        # tCount += 1
                        # return tCount

            if deepFlag:
                pass  # 评论信息
            return 1
        else:
            return -1
    else:
        return 0

def crawleTimelines_batch(browser, fbUser, deepFlag=False):
    logHelper.getLogger().info("Try to crawle the timeline info of " + fbUser.fbid)
    # tab_timeline = FBHelper.find_element(browser,\
    #                                      '//ul[@id = "u_0_m"]/li/a[@data-tab-key="timeline"]', \
    #                                      "TAB timeline is NOT found!")
    tab_timeline = FBHelper.find_element(browser, \
                                         '''//div[@id="fbTimelineHeadline"]/div[@class="_70k"]/
    ul[@data-referrer="timeline_light_nav_top"]/li/a[@data-tab-key="timeline"]''', \
                                         "TAB timeline is NOT found!")
    if tab_timeline is None:
        return -1

    # time.sleep(random.randint(2, 6))
    # tab_timeline.click()
    if not FBHelper.eleClick(tab_timeline):
        logHelper.getLogger().warning(
            "Stop to crawle the timeline info of %s because of status of your network!" % fbUser.fbid)
        return -1
    scroll2Bottom(browser, 1)
    FBHelper.save2Html(browser, fbUser.fbid, 'timeline')
    # time.sleep(random.randint(1, 4))

    # div[@class="fbUserContent _5pcr"]  还有可能为 class="_5pcr fbUserPost",_5pcr fbUserStory
    # 他往上两级 节点可以获取该timeline 的id
    eleList = FBHelper.find_element(browser, \
                                    r'''//div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent") or contains(@class,"fbUserStory"))]
                                    /../..''', \
                                    "No timeline is found!", \
                                    "find_elements_by_xpath")

    if eleList is None:
        logHelper.getLogger().warning('noooooo,the xpath of timeline may change')
        return -1

    tCount = 0
    if len(eleList) > 0:
        fbuserhelper = FBUserHelper.FBUserHelper()
        lstTimeDicResult = []
        lstLikerelationDicResult = []
        logHelper.getLogger().info(str(len(eleList)) + ' timeline are found')
        logHelper.getLogger().info('Begin to crawle timeline detail information!')
        for i, tmpItem in enumerate(eleList):
            # tCount += extractTLInfo(browser, fbUser, fbuserhelper, tmpItem, i, deepFlag=deepFlag)
            # batch start
            tc,dicReslutTime,dicResultLike = extractTLInfoSingle(browser, fbUser,tmpItem, i, deepFlag=deepFlag)
            tCount += tc
            if len(dicReslutTime) > 0:
                lstTimeDicResult.append(dicReslutTime)
            if len(dicResultLike) > 0:
                lstLikerelationDicResult.append(dicResultLike)
        fbuserhelper.Save_tb_user_timeline_batch(lstTimeDicResult)
        fbuserhelper.Save_tb_user_relationship_batch(lstLikerelationDicResult)
        # batch end

        logHelper.getLogger().info('Successfully crawled %s timelines of %s' % (tCount, fbUser.fbid))

    return tCount  # 数字表示正确爬取了几条动态信息
    # else:
    #     return "0" # 字符0 表示没有找 一条动态信息

    # logHelper.getLogger().info('Successfully crawled %s timelines of %s' % (tCount, fbUser.fbid))

def extractTLInfoSingle(browser, fbUser, TLNode, i, bTimestamp=0, deepFlag=False):
    timelineDicRes = {}
    likeRelationRes = {}

    logHelper.getLogger().info(str(i + 1) + 'th timeline info: ')
    # idNode = FBHelper.find_element(tmpItem,
    #                                './parent/parent',
    #                                str(i + 1) + "th timeline's id is not found!")
    # if idNode is None:
    #     continue
    tlID = TLNode.get_attribute("id")
    # FBHelper.find_element(tmpItem,'./parent/parent',
    #                       str(i + 1) + "th timeline's id is not found!")
    #  105 friends posted on Indraveer's Timeline 没有 id为空，过滤掉
    #  只找自己发的
    if tlID is not None and tlID.strip() != "":
        logHelper.getLogger().info("timelineID:" + tlID)
        timeStamp = TLNode.get_attribute("data-time")
        if int(timeStamp) > bTimestamp:
            rIDNode = FBHelper.find_element(TLNode, \
                                            r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent") or contains(@class,"fbUserStory"))]
                                            //div/form/input[2]''', \
                                            str(i + 1) + "th timeline's id node is not found!")
            timeNode = FBHelper.find_element(TLNode, \
                                             r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent") or contains(@class,"fbUserStory"))]
                                             //div[contains(@class,"_1dwg") and contains(@class,"_1w_m")]
                                             //abbr[@data-utime]''', \
                                             str(i + 1) + "th timeline's post time is not found!")

            # @ class ="_5pbx userContent"
            contentNode = FBHelper.find_element(TLNode, \
                                                r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent") or contains(@class,"fbUserStory"))]
                                                //div[contains(@class,"_1dwg") and contains(@class,"_1w_m")]
                                                //div[contains(@class,"userContent")]''', \
                                                str(i + 1) + "th timeline's has not text content!")
            #  图片  class="_3x-2"
            imgNodes = FBHelper.find_element(TLNode,
                                             r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent") or contains(@class,"fbUserStory"))]
                                              //div[contains(@class,"_1dwg") and contains(@class,"_1w_m")]
                                              //div[contains(@class,"_3x-2")]//a//img''',
                                             str(i + 1) + "th timeline's has not images!",
                                             "find_elements_by_xpath", )
            landMarkNode = FBHelper.find_element(TLNode, \
                                                 r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent") or contains(@class,"fbUserStory"))]
                                                  //div[contains(@class,"_1dwg") and contains(@class,"_1w_m")]
                                                  //span[contains(@class,"fwn") and contains(@class,"fcg")]/span[@class ="fcg"]/a''',
                                                 str(i + 1) + "th timeline's has no landmark")

            DZanNode = FBHelper.find_element(TLNode, \
                                             r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent") or contains(@class,"fbUserStory"))]
                                             //form[contains(@class,"commentable_item")]
                                             //span[contains(@class,"_4arz")]/span''',
                                             str(i + 1) + "th timeline's has no DZinfo")
            rTLID = ""
            if rIDNode is not None:
                rTLID = rIDNode.get_attribute('value')
                # 有可能是这种: ID,100001993779540:764304213646031:188881761160470:725875200
                rTLID = rTLID.split(':')[0][0:48]
                logHelper.getLogger().info("timeline ID:" + rTLID)

            postTime = ""
            if timeNode is not None:
                postTime = timeNode.get_attribute('title')
                postTime = TimeHelper.getDBTimeStr(postTime)
                logHelper.getLogger().info("time:" + postTime)
                # 66733642
            content = ""
            if contentNode is not None:
                content = contentNode.text
                # logHelper.getLogger().info("content:" + content)

            imgLink = ""
            imgAlt = ""
            if imgNodes is not None and len(imgNodes) > 0:
                for j, imageItem in enumerate(imgNodes):
                    imgLink += imageItem.get_attribute("src") + ";"
                    imgAlt += imageItem.get_attribute("alt") + ";"

            landName = ""
            landMarkID = ""
            if landMarkNode is not None:
                landName = landMarkNode.text
                # 除了地点还有可能是这种# Binay Shakya added 2 new photos.
                try:
                    landMarkID = \
                        landMarkNode.get_attribute('data-hovercard').split("?")[-1].split("&")[0].split("=")[-1]
                except Exception as e:
                    logHelper.getLogger().warning(e)
                    logHelper.getLogger().info("the element in that lacation is not landmark but others!")

            DZCount = 0
            if DZanNode is not None:
                try:
                    DZCount = DZanNode.text.replace(",", "").replace(".", "").lower().strip()
                    if DZCount != "":
                        if DZCount[-1] == 'k':
                            DZCount = DZCount[0:-1] + "000"
                        elif DZCount[-1] == 'm':
                            DZCount = DZCount[0:-1] + "000000"
                        DZCount = int(DZCount)
                        logHelper.getLogger().info("This timelime of %s has %s DZanCount!" % (fbUser.fbid, DZCount))
                    else:
                        DZCount = 0
                except Exception as e:
                    DZCount = 0
                    logHelper.getLogger().warning(e)
                    logHelper.getLogger().info("Failed to crawle the DZCount of this  timeline of %s!" \
                                               % fbUser.fbid)
            # 保存timelime
            dicResult = {'TimelineFBID': rTLID, 'postUserFBID': fbUser.fbid, 'postUserName': fbUser.name, \
                         'postTime': postTime, 'content': content, 'picturesURLs': imgLink, 'picturesAlts': imgAlt, \
                         'DZanCount': int(DZCount), 'landMarkID': landMarkID, \
                         'landMarkName': landName, 'timestamp': int(timeStamp)}
            timelineDicRes = dicResult.copy()
            # fbuserhelper.Save_tb_user_timeline(dicResult)

            # 深度采集，获取点赞人数，更细节的话可以获取 like  love wow等人数
            if deepFlag and DZanNode is not None:
                if FBHelper.eleClick(DZanNode):
                    browser.switch_to_alert()
                    # firstDZPeopleWndEle = FBHelper.find_element(browser,'''//div[contains(@class,"_4-i2") and contains(@class,"_50f4")]
                    #                                      //div[contains(@class,"uiScrollableArea")]
                    #                                      //div[contains(@class,"uiScrollableAreaBody")]
                    #                                      //ul[contains(@class,"uiList") and contains(@class,"_4kg")]
                    #                                      /li[contains(@class,"_5i_q")]''',
                    #                             'alertWndEle can not be found!')
                    #
                    # if firstDZPeopleWndEle is not None:
                    #     ActionChains(browser).move_to_element(firstDZPeopleWndEle).perform()
                    while True:
                        # scroll2Bottom(browser)
                        seeMoreNode = FBHelper.find_element(browser,
                                                            '''//div[contains(@class,"_4-i2") and contains(@class,"_50f4")]
                                                            //div[contains(@class,"uiScrollableArea")]
                                                            //div[contains(@class,"uiScrollableAreaBody")]
                                                            //div[contains(@class,"uiMorePager")]
                                                            //a[contains(text(), "See More")]''',
                                                            "the See More button can not be found!")
                        # seeMoreNode = FBHelper.find_element(browser,
                        #                         '''//a[contains(text(), "See More")]''',
                        #                         "the See More button can not be found!")
                        if seeMoreNode is None:
                            break
                        else:
                            FBHelper.eleClick(seeMoreNode)
                            # time.sleep(1)
                            time.sleep(3)  # yyyy
                    DZanList = FBHelper.find_element(browser,
                                                     '''//div[contains(@class,"_4-i2") and contains(@class,"_50f4")]
                                                         //div[contains(@class,"uiScrollableArea")]
                                                         //div[contains(@class,"uiScrollableAreaBody")]
                                                         //ul[contains(@class,"uiList") and contains(@class,"_4kg")]
                                                         /li[contains(@class,"_5i_q")]''',
                                                     "the DZan List can not be found!",
                                                     "find_elements_by_xpath")
                    if DZanList is not None and len(DZanList) > 0:
                        if len(DZanList) != DZCount:
                            logHelper.getLogger().warning(
                                "the number of DZan peoples is unequal the tatal Number!")
                        dicResult = {'fbida': rTLID, "namea": fbUser.name, 'relationtype': "Timeline.LIKE"}
                        for j, pItem in enumerate(DZanList):
                            logHelper.getLogger().info("get %sth DZan people info." % str(j + 1))
                            curPeople = FBHelper.find_element(pItem,
                                                              '''.//div[contains(@class,"_6a") and contains(@class,"_6b")]
                                                              //div[contains(@class,"fsl") and contains(@class,"fwb") and contains(@class,"fcb")]
                                                              //a''',
                                                              "the %sth DZan people can not be found!" % j)
                            # data - hovercard = "/ajax/hovercard/user.php?id=100002593093964&extragetparams=%7B%22hc_location%22%3A%22profile_browser%22%7D"
                            try:
                                DZfbid = curPeople.get_attribute("data-hovercard").split("?")[-1] \
                                    .split("&")[0].split("=")[-1]
                                if DZfbid.strip() != "" and curPeople.text.strip() != "":
                                    dicResult['fbidb'] = DZfbid
                                    dicResult['nameb'] = curPeople.text.strip()
                                    # fbuserhelper.Save_tb_user_relationship(dicResult)
                                    likeRelationRes = dicResult.copy()
                            except Exception as e:
                                logHelper.getLogger().error(e)
                                logHelper.getLogger().warning("Failed to extract %sth DZan people info!" % j)

                    # 关闭点赞细节窗口
                    # browser.close()
                    #  role="button" href="#" title="Close"  Close
                    closeNode = FBHelper.find_element(browser,
                                                      '''//div[contains(@class,"_4-i2") and contains(@class,"_50f4")]
                                                      //a[contains(text(), "Close")]''',
                                                      "Close button can not be found!")

                    if closeNode is not None:
                        FBHelper.eleClick(closeNode)
                        # tCount += 1
                        # return tCount

            if deepFlag:
                pass  # 评论信息
            return 1,timelineDicRes,likeRelationRes
        else:
            return -1,timelineDicRes,likeRelationRes
    else:
        return 0,timelineDicRes,likeRelationRes

# not used until now
def fetchNewTimelines(browser, fbUser, timeStamp, deepFlag=False):
    fbuserhelper = FBUserHelper.FBUserHelper()
    browser.get("https://www.facebook.com/%s" % fbUser.fbid)
    bInt = int(timeStamp)
    logHelper.getLogger().info("Try to fetch new timeline info of " + fbUser.fbid)

    initIdx = 0
    fCount = 0
    logHelper.getLogger().info('Begin to fetch new timeline of %s!' % fbUser.fbid)
    while True:
        eleList = FBHelper.find_element(browser, \
                                        r'''//div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") 
                                        or contains(@class,"fbUserContent"))]/../..''', \
                                        "No timeline is found!", \
                                        "find_elements_by_xpath")

        if eleList is None or len(eleList) <= initIdx:
            logHelper.getLogger().info('Fetch %s new timelines of %s!' % (fCount, fbUser.fbid))
            break

        stopFlag = False
        for idx in range(initIdx, len(eleList)):
            tmpItem = eleList[idx]
            rst = extractTLInfo(browser, fbUser, fbuserhelper, tmpItem, idx, bInt, deepFlag=deepFlag)
            if rst == -1:
                stopFlag = True
                break
            fCount += 1

            # tlID = tmpItem.get_attribute("id")
            # logHelper.getLogger().info(str(idx + 1) + 'th new timeline info:')
            # #  105 friends posted on Indraveer's Timeline 这个很恶心  没有 id为空，过滤掉
            # #  只找  自己发的
            # if tlID is not None and tlID != "":
            #     curInt = int(tmpItem.get_attribute("data-time"))
            #     if curInt > bInt:
            #         fCount += 1
            #         logHelper.getLogger().info("timelineID:" + tlID)
            #         f.write("timelineID:" + tlID)
            #         f.write(os.linesep)
            #         timeStamp = tmpItem.get_attribute("data-time")
            #         f.write("timeStamp:" + timeStamp)
            #         f.write(os.linesep)
            #         timeNode = FBHelper.find_element(tmpItem, \
            #                                          r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent"))]
            #                                          //div[contains(@class,"_1dwg") and contains(@class,"_1w_m")]
            #                                          //abbr[@data-utime]''', \
            #                                          str(idx + 1) + "th timeline's post time is not found!")
            #
            #         # @ class ="_5pbx userContent"
            #         contentNode = FBHelper.find_element(tmpItem, \
            #                                             r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent"))]
            #                                             //div[contains(@class,"_1dwg") and contains(@class,"_1w_m")]
            #                                             //div[contains(@class,"userContent")]''', \
            #                                             str(idx + 1) + "th timeline's has not text content!")
            #         landMarkNode = FBHelper.find_element(tmpItem, \
            #                                              r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent"))]
            #                                               //div[contains(@class,"_1dwg") and contains(@class,"_1w_m")]
            #                                               //span[contains(@class,"fwn") and contains(@class,"fcg")]/span[@class ="fcg"]/a''',
            #                                              str(idx + 1) + "th timeline's has no landmark")
            #         DZanNode = FBHelper.find_element(tmpItem, \
            #                                          r'''./*/div[contains(@class,"_5pcr") and (contains(@class,"fbUserPost") or contains(@class,"fbUserContent"))]
            #                                          //form[contains(@class,"commentable_item")]
            #                                          //span[contains(@class,"_4arz")]/span''',
            #                                          str(idx + 1) + "th timeline's has no DZinfo")
            #
            #         if timeNode is not None:
            #             postTime = timeNode.get_attribute('title')
            #             logHelper.getLogger().info("time:" + postTime)
            #             f.write("time:" + postTime)
            #             f.write(os.linesep)
            #             # 66733642
            #         if contentNode is not None:
            #             content = contentNode.text
            #             # logHelper.getLogger().info("content:" + content)
            #             f.write("content:" + content)
            #             f.write(os.linesep)
            #
            #         if landMarkNode is not None:
            #             landName = landMarkNode.text
            #             landMarkID = \
            #             landMarkNode.get_attribute('data-hovercard').split("?")[-1].split("&")[0].split("=")[-1]
            #             if landMarkID != "":
            #                 f.write("landMarkID:" + landMarkID)
            #                 f.write(os.linesep)
            #                 f.write("landName:" + landName)
            #                 f.write(os.linesep)
            #
            #         if DZanNode is not None:
            #             DZCount = DZanNode.text
            #             # landMarkNode.get_attribute('data-hovercard').split("?")[-1].split("&")[0].split("=")[-1]
            #             if DZCount != "":
            #                 f.write("DZCount:" + DZCount)
            #                 f.write(os.linesep)
            #
            #         # if contentNode is not None or timeNode is not None:
            #         f.write("=====================================================================")
            #         f.write(os.linesep)
            #     else:
            #         stopFlag = True
            #         break

        initIdx = len(eleList)
        if stopFlag:
            logHelper.getLogger().info('Fetch %s new timelines of %s!' % (fCount, fbUser.fbid))
            break
        else:
            scroll2Bottom(browser, 1)  # 往下拖动，继续获取timeline


def crawleImage(browser, fbUser):
    imgNode = FBHelper.find_element(browser,
                                    # r'//div[@id="fbTimelineHeadline"]/div[@class="name"]/div[@class="photoContainer"]/a/img',
                                    r'//div[@id="fbTimelineHeadline"]//div[@class="photoContainer"]/div/a/img',
                                    )
    if imgNode is None:
        return False

    imgUrl = imgNode.get_attribute('src')
    return FBHelper.saveImg(imgUrl, 'images' + os.path.sep + fbUser.fbid + ".jpg")


def crawleAbout(browser, fbUser):
    logHelper.getLogger().info("Try to crawle the about info of " + fbUser.fbid)
    # tab_timeline = FBHelper.find_element(browser,\
    #                                      '//ul[@id = "u_0_m"]/li/a[@data-tab-key="timeline"]', \
    #                                      "TAB timeline is NOT found!")
    tab_about = FBHelper.find_element(browser, \
                                      '''//div[@id="fbTimelineHeadline"]/div[@class="_70k"]/
 ul[@data-referrer="timeline_light_nav_top"]/li/a[@data-tab-key="about"]''', \
                                      "TAB about is NOT found!")
    if tab_about is None:
        return -1

    # time.sleep(random.randint(1, 4))
    # tab_about.click()
    if not FBHelper.eleClick(tab_about):
        logHelper.getLogger().warning(
            "Stop to crawle the about info of %s because of status of your network!" % fbUser.fbid)
        return -1

    # time.sleep(random.randint(3, 7))
    FBHelper.save2Html(browser, fbUser.fbid, "about")

    AboutNav = FBHelper.find_element(browser, r'//ul[@data-testid="info_section_left_nav"]')

    if AboutNav is None:
        return -1

    # 页面一切正常
    # RDList = getShuffledList(7)
    RDList = getShuffledList(8)

    fbuserhelper = FBUserHelper.FBUserHelper()
    Name = fbUser.name
    if fbUser.name.strip() == "":
        nameNode = FBHelper.find_element(browser,
                                         "//div[contains(@class,'cover')]//div/h1/a",
                                         "name Node can not be found!")
        if nameNode is not None:
            Name = nameNode.text
    FBHomepage = browser.current_url
    if FBHomepage.find('/profile.php') >= 0:
        FBHomepage = "https://www.facebook.com/%s" % fbUser.fbid

    if FBHomepage.find('/about?') >=0:
        p = FBHomepage.find('/about?')
        FBHomepage = FBHomepage[:p]

    # LogoFile = "\\images\\%s.jpg" % fbUser.fbid
    LogoFile = ""
    Gender = ""
    Birthday = ""
    Work = ""
    EDU = ""
    currentCity = ""
    homeTown = ""
    phone = ""
    Languages = ""
    email = ""
    interestedIn = ""
    # FriendsCount            = ""
    homePageUrl = ""
    favoriteQuotes = ""
    selfIntro = ""
    lifeEvents = ""
    Relationship = ""
    DESC = ""
    Relationship = ""
    iType = 0
    imgNode = FBHelper.find_element(browser,
                                    # r'//div[@id="fbTimelineHeadline"]/div[@class="name"]/div[@class="photoContainer"]/a/img',
                                    r'//div[@id="fbTimelineHeadline"]//div[@class="photoContainer"]/div/a/img',
                                    )
    if imgNode is not None:
        LogoFile = imgNode.get_attribute('src')
         
    for idx in RDList:
        if idx == 1:  # Work and Education or Work and education
            title = "Work and education"
            jumpFlag = jump_AboutInfo(browser, title, fbUser.fbid)
            if not jumpFlag:
                title = "Work and Education"
                jumpFlag = jump_AboutInfo(browser, title, fbUser.fbid)

            if jumpFlag:
                WorkNodes = FBHelper.find_element(browser,
                                                  r'//div[@id="pagelet_eduwork"]/div/div[@data-pnref="work"]/ul/li',
                                                  "The Content of Work is not found!",
                                                  "find_elements_by_xpath")
                EduNodes = FBHelper.find_element(browser,
                                                 r'//div[@id="pagelet_eduwork"]/div/div[@data-pnref="edu"]/ul/li',
                                                 "The Content of Edu is not found!",
                                                 "find_elements_by_xpath")
                if WorkNodes is not None:
                    for i, tItem in enumerate(WorkNodes):
                        Work += tItem.text.replace("\n", "\t") + os.linesep
                    logHelper.getLogger().info("Crawle the Work info of " + fbUser.fbid + " is completed!")

                if EduNodes is not None:
                    for i, tItem in enumerate(EduNodes):
                        EDU += tItem.text.replace("\n", "\t") + os.linesep
                    logHelper.getLogger().info("Crawle the Edu info of " + fbUser.fbid + " is completed!")

                iType += 1
        elif idx == 2:  # Places He's Lived
            title = "Places "
            jumpFlag = jump_AboutInfo(browser, title, fbUser.fbid)
            if jumpFlag:
                PLContentNodes = FBHelper.find_element(browser, r'//div[@id="pagelet_hometown"]//ul/li',
                                                       "The Content of Places He's Lived is not found!",
                                                       "find_elements_by_xpath")
                if PLContentNodes is not None:
                    for tmpItem in PLContentNodes:
                        if tmpItem.text.find("Current city") > 0:
                            currentCity += tmpItem.text.replace("Current city", "").replace("\n", "") + os.linesep
                        elif tmpItem.text.find("Hometown") > 0:
                            homeTown += tmpItem.text.replace("Hometown", "").replace("\n", "") + os.linesep
                        else:
                            DESC += tmpItem.text + ";"

                    logHelper.getLogger().info("Crawle the Places He's Lived info of " + fbUser.fbid + " is completed!")
                    iType += 1
        elif idx == 3:  # Contact and Basic Info or contact and basic info
            title = "Contact and basic info"
            jumpFlag = jump_AboutInfo(browser, title, fbUser.fbid)
            if not jumpFlag:
                title = "Contact and Basic Info"
                jumpFlag = jump_AboutInfo(browser, title, fbUser.fbid)
            if jumpFlag:
                contactContentNodes = FBHelper.find_element(browser, r'//div[@id="pagelet_contact"]//ul/li',
                                                            "The Content of Contact and Basic Info is not found!",
                                                            "find_elements_by_xpath")
                basicContentNodes = FBHelper.find_element(browser, r'//div[@id="pagelet_basic"]//ul/li',
                                                          "The Content of Contact and Basic Info is not found!",
                                                          "find_elements_by_xpath")
                # f = open("crawledInfo" + os.sep + fbid + '_About.txt', 'a', encoding='utf-8')
                if contactContentNodes is not None:
                    for tmpItem in contactContentNodes:
                        # Address  Mobile Phones  Facebook
                        tmpStr = tmpItem.text.replace("\n", "")
                        if tmpStr.find("Mobile Phones") >= 0:
                            phone += tmpStr.replace("Mobile Phones", "") + ";"
                        elif tmpStr.find("Email") >= 0:
                            email += tmpStr.replace("Email", "") + ";"
                        elif tmpStr != "No contact info to show":
                            DESC += tmpStr + ";"

                if basicContentNodes is not None:
                    for tmpItem in basicContentNodes:
                        tmpStr = tmpItem.text.replace("\n", "")
                        # //Religious Views  宗教观 https://www.facebook.com/hookhow
                        # Political Views  政治观
                        if tmpStr.find("Gender") >= 0:
                            Gender = tmpStr.replace("Gender", "")
                        elif tmpStr.find("Languages") >= 0:
                            Languages += tmpStr.replace("Languages", "")
                        elif tmpStr.find("Birthday") >= 0:
                            Birthday += tmpStr.replace("Birthday", "")
                        elif tmpStr.find("Interested In") >= 0:
                            interestedIn += tmpStr.replace("Interested In", "")
                        else:
                            DESC += tmpStr + ";"

                if contactContentNodes is not None or basicContentNodes is not None:
                    iType += 1
                    logHelper.getLogger().info("Crawle the %s info of %s is completed!" % (title, fbUser.fbid))
                else:
                    logHelper.getLogger().info("Failed to crawle the %s info of %s" % (title, fbUser.fbid))
                    # pass
        elif idx == 4:  # Family and Relationships or Family and relationships
            title = "Family and relationships"
            jumpFlag = jump_AboutInfo(browser, title, fbUser.fbid)
            if not jumpFlag:
                title = "Family and Relationships"
                jumpFlag = jump_AboutInfo(browser, title, fbUser.fbid)
            if jumpFlag:
                RelationNodes = FBHelper.find_element(browser,
                                                      r'//div[@id="pagelet_relationships"]/div[1 and contains(@class,"editAnchor")]/ul/li',
                                                      "The Content of Relationships is not found!",
                                                      "find_elements_by_xpath")
                FamilyMembersNodes = FBHelper.find_element(browser,
                                                           r'//div[@id="pagelet_relationships"]/div[2 and contains(@data-pnref,"family")]//ul/li',
                                                           "The Content of Family Members is not found!",
                                                           "find_elements_by_xpath")
                #  区分  Relationship   和家庭成员
                if RelationNodes is not None:
                    for rel in Relationship:
                        if rel.text.find("No relationship info to show") < 0:
                            Relationship += rel.text
                    logHelper.getLogger().info("Crawle the relationships info of %s is completed!" % fbUser.fbid)

                if FamilyMembersNodes is not None:
                    # "https://www.facebook.com/chinnuv1/"有很多家庭成员
                    iFamily = 0
                    #  爬取的数据存放地
                    sData = {}
                    sData['fbida'] = fbUser.fbid
                    sData['namea'] = fbUser.name
                    # sData['priority']       = fbUser.priority - 1
                    sData['deep'] = fbUser.deep + 1
                    sData['Description'] = ""
                    for tmpItem in FamilyMembersNodes:
                        sData['fbidb'] = ""
                        sData['nameb'] = ""
                        sData['relationtype'] = ""
                        nameNode = FBHelper.find_element(tmpItem,
                                                         '''.//div[contains(@class,"_6a")]
                                                          /div[contains(@class,"_6a") and contains(@class,"_6b")]
                                                          /div[contains(@class,"fsm") and contains(@class,"fwn") and contains(@class,"fcg")]
                                                          /span/a''',
                                                         "The Family member Name Node can not be found!")
                        # /div[2 and contains(@class,"fsm") and contains(@class,"fwn") and contains(@class,"fcg")]''',
                        # 其实找的是第一个
                        #  索引 不能和其他属性混在一块。
                        relNode = FBHelper.find_element(tmpItem,
                                                        '''.//div[contains(@class,"_6a")]
                                                         /div[contains(@class,"_6a") and contains(@class,"_6b")]
                                                         /div[2]''',
                                                        "The Family Relation Node can not be found!")
                        if nameNode is not None and relNode is not None:
                            sData['fbidb'] = nameNode.get_attribute("data-hovercard").split("=")[-1]
                            sData['nameb'] = nameNode.text
                            # https://www.facebook.com/howard.cheng.9
                            sData['homepage'] = nameNode.get_attribute('href')
                            if sData['homepage'].find('profile.php?id') >= 0:
                                sData['homepage'] = 'www.facebook.com/%s' % sData['fbidb']
                            sData['relationtype'] = "FamilyMembers." + relNode.text
                            # 保存家庭成员同时保存关系
                            sData['priority'] = Analyzer.computerPriority(fbUser, sData['Description'], sData['deep'])
                            saveFriends(fbuserhelper, sData)
                            iFamily += 1
                    logHelper.getLogger().info("Successfully Crawled %s FamilyMembers of %s!" % (iFamily, fbUser.fbid))

                if FamilyMembersNodes is None and RelationNodes is None:
                    logHelper.getLogger().info("Failed to crawle the %s info of %s" % (title, fbUser.fbid))
                else:
                    iType += 1
                    logHelper.getLogger().info("Crawle the %s info of %s is completed!" % (title, fbUser.fbid))

        elif idx == 5:  # Details About Indraveer
            title = "Details About"
            jumpFlag = jump_AboutInfo(browser, title, fbUser.fbid)
            if jumpFlag:
                BIContentNodes = FBHelper.find_element(browser, r'//div[@id="pagelet_bio"]//ul/li',
                                                       "The Content of Details About is not found!",
                                                       "find_elements_by_xpath")
                FQuotesNodes = FBHelper.find_element(browser, r'//div[@id="pagelet_quotes"]//ul/li',
                                                     "The Content of Favorite Quotes is not found!",
                                                     "find_elements_by_xpath")

                if BIContentNodes is not None:
                    for tmpItem in BIContentNodes:
                        selfIntro += tmpItem.text + os.linesep
                if FQuotesNodes is not None:
                    for tmpItem in FQuotesNodes:
                        favoriteQuotes += tmpItem.text + os.linesep
                if FQuotesNodes is not None or BIContentNodes is not None:
                    iType += 1
                    logHelper.getLogger().info("Crawle the %s info of %s is completed!" % (title, fbUser.fbid))
                else:
                    logHelper.getLogger().info("Failed to crawle the %s info of %s" % (title, fbUser.fbid))
        elif idx == 6:  # Life Events
            title = "Life events"
            jumpFlag = jump_AboutInfo(browser, title, fbUser.fbid)
            if jumpFlag:
                LEContentNodes = FBHelper.find_element(browser, r'//div[@class="_4qm1"]/ul/li',
                                                       "The Content of Life Events is not found!",
                                                       "find_elements_by_xpath")
                if LEContentNodes is not None:
                    for tmpItem in LEContentNodes:
                        lifeEvents += tmpItem.text.replace("\n", ":") + os.linesep
                    iType += 1
                    logHelper.getLogger().info("Crawle the %s info of %s is completed!" % (title, fbUser.fbid))
                else:
                    logHelper.getLogger().info("Failed to crawle the %s info of %s" % (title, fbUser.fbid))
        elif idx == 7:
            pass
        else:
            # OTHER
            pass
        time.sleep(random.randint(3, 5))  # yyyy
    # 保存个人详细信息
    if favoriteQuotes.find("No favorite quotes to show") >= 0:
        favoriteQuotes = ""
    if selfIntro.find('No additional details to show') >= 0:
        selfIntro = ''
    # if
    dicResult = {'fbid': fbUser.fbid, 'Name': Name, 'fbHomepage': FBHomepage,
                 'logoFile': LogoFile, 'Gender': Gender, 'rank': 3, 'Birthday': Birthday,
                 'Work': Work, 'EDU': EDU, 'currentCity': currentCity,
                 'homeTown': homeTown, 'phone': phone,
                 'Languages': Languages, 'email': email,
                 'interestedIn': interestedIn, 'homePageUrl': homePageUrl,
                 'favoriteQuotes': favoriteQuotes, 'selfIntro': selfIntro,
                 'lifeEvents': lifeEvents, 'Description': DESC, 'Relationship': Relationship}
    fbuserhelper.Save_tb_user_info(dicResult)


def jump_AboutInfo(browser, title, fbid):
    logHelper.getLogger().info("Try to crawle the %s  info of %s" % (title, fbid))
    NavItemNode = FBHelper.find_element(browser,
                                        r'//ul[@data-testid="info_section_left_nav"]/li[starts-with(@title,"%s")]' % title,
                                        "Nav Item of %s is not found!" % title)
    if NavItemNode is None:
        logHelper.getLogger().info("Failed to crawle the %s info of %s" % (title, fbid))
        return False

    # NavItemNode.click()
    if not FBHelper.eleClick(NavItemNode):
        logHelper.getLogger().warning("Stop to crawle %s info of %s because of status of your network!" % (title, fbid))
        return False
    time.sleep(random.random())
    FBHelper.save2Html(browser, fbid, "About_" + title)
    return True

def LogOut(browser, menuTag="", itemTag=""):
    try:

        # locate Menu
        menuTag = "//a[@id='pageLoginAnchor']"

        ele = browser.find_element_by_xpath(menuTag)
        ele.click()
        time.sleep(10)
        # locate item
        itemTag = "//div[@id='BLUE_BAR_ID_DO_NOT_USE']//ul[@role='menu']/li[last()]/a"

        eleCLick = browser.find_element_by_xpath(itemTag)
        eleCLick.click()
        time.sleep(5)
        return True
    except TimeoutException as e1:
        # logHelper.getLogger().debug(e1)
        return False

if __name__ == '__main__':
    browser = webdriver.Firefox()

    time.sleep(2)
    browser.close()
    browser = None
    if browser == None: 
        print('OK')

    '''
    # fbAccount = ourFBAccount('trumpJACK2018@outlook.com', '1qaz@WSX3edc', None)
    fbAccount = OurFBAccount.getAccount('ourFBAccount.txt')
    # logName = time.strftime('%Y-%M-%d', time.localtime(time.time())) + ".log"
    logName = 'myLog'
    myargs = {'fName': logName, 'fLevel': logging.DEBUG}
    logger = logHelper.getLogger('myLog', logging.INFO, **myargs)

    # 和上次log隔开
    logger.info("============================================================")
    browser, loginFlag = initCrawler("https://www.facebook.com/", fbAccount)
    if not isLogin:
        logHelper.getLogger().info("now exit the programme!")
        exit(1)

    # # 监控，取新的timeline
    # browser.get("https://www.facebook.com/100010661110932")
    fbUser = FBBaseUser('100001689754436', '莊宜璇', 0)
    crawleInfo(browser, fbUser, fbAccount)
    # fetchNewTimelines(browser,fbUser,"1486400954")
    '''
    # # 简单爬取
    # while True:
    #     now = datetime.datetime.now()
    #     if now.hour > 1 and now.hour < 5:
    #         time.sleep(60)
    #         continue
    #
    #     r = SqliteHelper().fetchTask()
    #     if r is None:
    #         logHelper.getLogger().info("ALL TASK ARE COMPLETED!")
    #         time.sleep(3)
    #         browser.quit()
    #         break
    #     else:
    #
    #         if crawleInfo(browser, r[0], fbAccount) == 1:
    #             sqlStr = "UPDATE FBIDMetaInfo set isCrawled = ? WHERE fbid = ?"
    #             tmpData = ('1', r[0])
    #             SqliteHelper().execute(sqlStr, tmpData)
    #
    #             # # crawlerInfo(browser,'100008322095759',fbAccount)
    #             # # crawlerInfo(browser,'100003567040399',fbAccount)
    #             # # crawlerInfo(browser,'100003796006737',fbAccount)
    #             # # crawlerInfo(browser,'100014995573258',fbAccount)
    #             # # crawlerInfo(browser,'100017274727394',fbAccount)
    #             # # crawlerInfo(browser,'100003853895761',fbAccount)
    #             # # crawlerInfo(browser,'100013644602274',fbAccount)
    #             # # crawlerInfo(browser,'100003287943061',fbAccount)
    #             # # crawlerInfo(browser, '100010733825080', fbAccount)
    #             # # crawlerInfo(browser,'100019528096170',fbAccount)



