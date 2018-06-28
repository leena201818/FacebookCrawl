# -*- coding: utf-8 -*-

import logging
import time
import random
import os
import json
import urllib
from urllib import request

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from loghelper.loghelper import logHelper


# # '''
# 基础工具类
# # '''
class OurFBAccount():
    u = ''
    p= ''
    fbid = ''
    # nickName = None
    def __init__(self,u,p,fbid):
        self.u = u
        self.p = p
        self.fbid = fbid
        # self.nickName = nickName

    @classmethod
    def getAccount(cls,fName):
        with open(fName,'r',encoding='utf-8') as f:
            dDict = {}
            for i, line in enumerate(f.readlines()):
                if i == 0:
                    continue
                str = line.strip()
                if str[0] == "#" or str == "":
                    continue
                else:
                    strLst = str.split(":")
                    dDict[strLst[0].strip()] = strLst[1].strip()
            account = OurFBAccount(dDict['user'], dDict['pwd'], dDict['fbid'])
            # if "nickName" not in dDict.keys():
            #     account = OurFBAccount(dDict['user'], dDict['pwd'],dDict['fbid'])
            # else:
            #     account = OurFBAccount(dDict['user'], dDict['pwd'],dDict['fbid'], dDict['nickName'])
            return account

#   FB用户 包含基本信息的类
class FBBaseUser():
    def __init__(self,id,name,deep,priority=None,desc=None):
        self.fbid       = id
        self.name       = name
        self.deep       = deep
        self.priority   = 0
        self.desc       = ""
        if priority is not None:
            self.priority = priority
        if desc is not None:
            self.desc = desc

class FBHelper():
    @staticmethod
    def find_element(onwer,lStr,wStr = 'Element can not be found',\
                     methodName = 'find_element_by_xpath'):
        rtnEle = None;
        try:
            #  隐式等待
            if isinstance(onwer,webdriver.Firefox):
                myWait = WebDriverWait(onwer, 15)
                myWait.until(EC.presence_of_element_located((By.XPATH, lStr)))
            if methodName == "find_element_by_xpath":
                rtnEle = onwer.find_element_by_xpath(lStr)
            elif methodName == "find_elements_by_xpath":
                rtnEle = onwer.find_elements_by_xpath(lStr)
            else:
                logHelper.getLogger().warning("Now do not support this method")
        except Exception as e:
            logHelper.getLogger().error(e)
            logHelper.getLogger().warning(wStr)

        return  rtnEle

    # 一直等待某元素可见，默认超时10秒
    @staticmethod
    def is_visible(browser,locator, timeout=15):
        try:
            WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except TimeoutException as e1:
            logHelper.getLogger().debug(e1)
            return False

    # 一直等待某个元素消失，默认超时10秒
    @staticmethod
    def is_not_visible(browser,locator, timeout=15):
        try:
            WebDriverWait(browser, timeout).until_not(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except TimeoutException as e1:
            logHelper.getLogger().debug(e1)
            return False

    @staticmethod
    def openUrl(browser,url,maxTryNum = 5):
        isSuccess = False
        i = 0;
        while i <= maxTryNum:
            try:
                browser.get(url)
                isSuccess = True
                break;
            except Exception as e:
                i += 1
                logHelper.getLogger().error(e)
                logHelper.getLogger().info("try to open the url: " + url + " " + str(i) + " times!")
                time.sleep(5)

        if isSuccess == False:
            logHelper.getLogger().warning("Can not open the url, please check you network!")
        return isSuccess

    def checkAccount(browser,url,maxTryNum = 5):
        isLoginSuccess = False
        i = 0;
        while i <= maxTryNum:
            try:
                browser.get(url)
                isLoginSuccess = True
                break;
            except Exception as e:
                i += 1
                logHelper.getLogger().error(e)
                logHelper.getLogger().info("try to open the url: " + url + " " + str(i) + " times!")
                time.sleep(5)

        if isLoginSuccess == False:
            logHelper.getLogger().warning("Can not open the url, please check you network!")
            return 'NetError'

        # https: // www.facebook.com / checkpoint /?next
        time.sleep(random.randint(2,4))
        cur_rul = browser.current_url
        if cur_rul.find(r'https://www.facebook.com/checkpoint') >= 0:
            logHelper.getLogger().warning('jump to the URL:https://www.facebook.com/checkpoint/?next')
            return 'OutAccountForbidden'

        #verify the account avalibale
        try:
            # < h2 class ="accessible_elem" > Sorry, this content isn't available at the moment</h2>
            # xpSorry = "//h2[@class='accessible_elem')]"

            xpSorry = "//i[contains(@class,'uiHeaderImage img')]"
            # xpSorry = "//i[@class='uiHeaderImage img sp_KShOXWot7St sx_50fa8a']"
            if FBHelper.is_visible(browser,xpSorry,10):
                logHelper.getLogger().warning("find the uiHeaderImage img(Sorry, this content isn't available at the moment)")
                # look for zuck 004
                time.sleep(random.randint(2,5))
                zuck = 'https://www.facebook.com/004'
                browser.get(zuck)
                if FBHelper.is_visible(browser,xpSorry,10):
                    return 'OutAccountForbidden'
                else:
                    return 'TargetFBIDInValid'
            else:
                logHelper.getLogger().debug("the html has no uiHeaderImage img,our account is normal.")
                return 'OK'

        except Exception as e:
            logHelper.getLogger().error(e)
        return 'OtherError'

    @staticmethod
    def openUrl_exit(browser,url,maxTryNum = 5):
        isOpened = FBHelper.openUrl(browser, url, maxTryNum)
        if isOpened == False:
            strF = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
            strF += "_" + str(random.randint(1,61))
            browser.save_screenshot("errorShot" + os.sep + strF + ".jpg")
            browser.quit()
            logHelper.getLogger().warning("Your network seems to have some promlem, please check it. Try to exit!")
            exit(1)

    @staticmethod
    def eleClick(eleNode):
        successFlag = False
        try:
            eleNode.click()
            successFlag = True
        except Exception as e:
            logHelper.getLogger().error(e)
            logHelper.getLogger().warning("please check status of your network!")
            successFlag = False
        return  successFlag

    # 保存原始页面
    @staticmethod
    def save2Html(browser,fbid,sName):
        return
        try:
            logHelper.getLogger().info("try to save the raw html page to file......")
            fName = fbid + "_" + sName + "_" + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) + ".html"
            with open("raw_page" + os.sep + fName, "w", encoding="utf-8") as f:
                f.write(browser.page_source)
            logHelper.getLogger().info("save the raw html page to file successfully!!")
        except Exception as e:
            logHelper.getLogger().info("save the raw html page to file Failed!!")

    # 传入图片地址，文件名，保存单张图片
    @staticmethod
    def saveImg(imageURL, fileName):
        try:
            heads = {"User-Agent": r"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"}
            req = request.Request(imageURL, headers=heads)
            u = urllib.request.urlopen(req)
            data = u.read()
            f = open(fileName, 'wb')
            f.write(data)
            f.close()
            return True
        except Exception as e:
            logHelper.getLogger().error(e)
            logHelper.getLogger().warning("failed to save the image to file %s" % fileName)
            return False

class TimeHelper():
    #    Monday, August 7, 2017 at 9:43am 时间字符串转化为时间
    #         %a 英文星期简写
    #         %A 英文星期的完全
    #         %b 英文月份的简写
    #         %B 英文月份的完全
    #         %c 显示本地日期时间
    #         %d 日期，取1 - 31
    #         %H 小时， 0 - 23
    #         %I 小时， 0 - 12
    #         %m 月， 01 - 12
    #         %M 分钟，1 - 59
    #         %j 年中当天的天数
    #         %w 显示今天是星期几
    #         %W 第几周
    #         %x 当天日期
    #         %X 本地的当天时间
    #         %y 年份 00 - 99 间
    #         %Y 年份的完整拼写
    #         %p  Locale's equivalent of either AM or PM.
    @staticmethod
    def getTimeFromStr(timeStr):
        tmpList = []
        if timeStr[-2:] == "am":
            time_struct = time.strptime(timeStr,"%A, %B %d, %Y at %H:%Mam")
            tmpList = [item for item in time_struct[0:6]]
        elif timeStr[-2:] == "pm":
            time_struct = time.strptime(timeStr,"%A, %B %d, %Y at %H:%Mpm")
            tmpList = [item for item in time_struct[0:6]]
            tmpList[-3] +=12
        else:
            logHelper.getLogger().warning("the string's format is not right!")
            # 返回当前时间
            curTime = datetime.datetime.now()
            tmpList = [cur.year,cur.month,cur.day,cur.hour,cur.minute,curTime.second]

        rtnList = tmpList[0:6]# [tmpList[3],tmpList[1],tmpList[2],tmpList[4],tmpList[5],0]
        return  rtnList

    @staticmethod
    def getStrFromList(timeList):
        timeStr = '%s-%s-%s %s:%s:%s' % tuple(timeList)
        return  timeStr

    @staticmethod
    def getDBTimeStr(timeStr):
        #    Monday, August 7, 2017 at 9:43am 时间字符串转化为时间
        rtnStr = time.strftime('%Y-%m-%d %H:%M:%S',time.strptime(timeStr, '%A, %B %d, %Y at %I:%M%p'))
        return rtnStr
        # tmpList = TimeHelper.getTimeFromStr(timeStr)
        # return  TimeHelper.getStrFromList(tmpList)

# 数据分析器
class Analyzer():
    keyWords1 = None  # 不区分大小写
    keyWords2 = None  # 区分大小写
    setStopWords = None  # stop words

    @classmethod
    def getKeyWords(cls):
        if cls.keyWords1 is None:
            keyWords1 = {}
            keyWords2 = {}
            keyWords3 = set()
            flag = 0
            with open("priority_keywords.txt",'r',encoding='utf-8') as f:
                for i,line in enumerate(f.readlines()):
                    line = line.strip()
                    if i==0:
                        continue
                    if len(line) == 0:
                        continue
                    if line[0] == "#":
                        if line.find("=====")>0:
                            flag += 1
                        continue
                    try:
                        strLst = line.split(":")
                        if flag == 0:
                            keyWords1[strLst[0].strip()] = int(strLst[1].strip())
                        elif flag == 1:
                            keyWords2[strLst[0].strip()] = int(strLst[1].strip())
                        elif flag == 2:
                            keyWords3.add(strLst[0].strip())
                    except Exception as e:
                        logHelper.getLogger().error(e)
                        logHelper.getLogger().warning('''Read the priority_keywords.txt has error!
                        the line content is: %s''' %line)
            cls.keyWords1 = keyWords1
            cls.keyWords2 = keyWords2
            cls.setStopWords = keyWords3
        return cls.keyWords1,cls.keyWords2,cls.setStopWords

    @classmethod
    def computerPriority_old(cls,fbUser,descStr,deep):
        rtnP = int(fbUser.priority/3)
        descStr_l = descStr.lower()
        dictOne,dictTwo,setStopWords = cls.getKeyWords()
        for keyWord in dictOne:
            if descStr_l.find(keyWord.lower())>=0:
                rtnP += dictOne[keyWord]
        for keyWord in dictTwo:
            if descStr.find(keyWord)>=0:
                rtnP += dictTwo[keyWord]

        rtnP -= 3*deep
        if rtnP >100:
            rtnP = 100
        return  rtnP

    @classmethod
    def computerPriority(cls,fbUser,descStr,deep):
        # remove the stop words firstly
        dictOne,dictTwo,setStopWords = cls.getKeyWords()
        for sw in setStopWords:
            descStr = descStr.replace(sw,'')

        rtnP = int(fbUser.priority/3)
        descStr_l = descStr.lower()

        for keyWord in dictOne:
            if len(keyWord.split()) == 1:  #one word
                words_descStr_l = descStr_l.split()
                if keyWord.lower() in words_descStr_l:
                    rtnP += dictOne[keyWord]
            else: # more than one word
                if descStr_l.find(keyWord.lower()) >= 0:
                    rtnP += dictOne[keyWord]

        for keyWord in dictTwo:
            if len(keyWord.split()) == 1:  #one word
                words_descStr = descStr.split()
                if keyWord in words_descStr:
                    rtnP += dictTwo[keyWord]
            else: # more than one word
                if descStr.find(keyWord) >= 0:
                    rtnP += dictTwo[keyWord]

        rtnP -= 3*deep
        if rtnP >100:
            rtnP = 100
        return  rtnP

if __name__ == "__main__":
    logName = time.strftime('%Y-%m-%d', time.localtime(time.time())) + ".log"
    myargs = {'fName': logName, 'fLevel': logging.DEBUG}
    logger = logHelper.getLogger('myLog', logging.INFO, **myargs)
    dictOne, dictTwo,stopWords = Analyzer.getKeyWords()

    descStr = 'Deputy General Manager (DGM) at Oil & Natural Gas Corp, India  '

    print(descStr)
    for sw in stopWords:
        descStr = descStr.replace(sw, '')
    print(descStr)

    # for keyWord in stopWords :
    #         print(keyWord)
    # print(len(dictOne))
    # print(len(dictTwo))

    pass

    # rtn = TimeHelper.getTimeFromStr("Monday, August 7, 2017 at 9:43am")
    # print(rtn)
    # print(TimeHelper.getStrFromList(rtn))
    # print("-".join(rtn))
    rtn = TimeHelper.getDBTimeStr("Monday, August 7, 2017 at 9:43pm")
    print(rtn)

    # account = OurFBAccount.getAccount("ourFBAccount.txt")
    # fbUser = FBBaseUser("11111111","shiyan",0,50)
    # p = Analyzer.computerPriority(fbUser,"MCTE",1)
    #
    # print(p)