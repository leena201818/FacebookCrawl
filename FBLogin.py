# -*- coding: utf-8 -*-
#  BY ZHAN 2017-07-28
import logging
import time
import random
import os
import json

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException

from loghelper.loghelper import logHelper
from utility import OurFBAccount
from utility import FBHelper


# # '''
# # 用户密码方式登录，nickName 登录用户的昵称可以帮助判断是否登录成功
# # 返回登录是否成功！
# # '''
def login_by_up(browser,myAccount,cookieFile,dictLogin):
    logHelper.getLogger().info('login_url: ' + browser.current_url)
    # print(browser.page_source)
    #### firefox取元素代码
    # try:
    #     user_input = browser.find_element_by_xpath(r'//input[@id="email"]')
    #     pwd_input = browser.find_element_by_xpath(r'//input[@id="pass"]')
    #     sub_btn = browser.find_element_by_xpath(r'//label[@id="loginbutton"]/input[@id="u_0_r"]')
    #     #### PhantomJS取元素代码
    #     # user_input = browser.find_element_by_xpath(r'//input[@name="email"]')
    #     # pwd_input = browser.find_element_by_xpath(r'//input[@name="pass"]')
    #     # sub_btn = browser.find_element_by_xpath(r'//button[@name="login"]')
    # except  NoSuchElementException as  e:
    #     logHelper.getLogger().debug('login element can not be found, please check whether the page is changed!')
    #     browser.quit()
    #     return  False

    uStr = dictLogin['uStr']
    pStr = dictLogin['pStr']
    lStr = dictLogin['lStr']
    user_input,pwd_input, sub_btn,  = findLoginInput(browser,uStr,pStr,lStr)

    if user_input is None or pwd_input is None or sub_btn is None:
        return

    executeLogin(user_input,myAccount.u, pwd_input, myAccount.p, sub_btn)

    loginSuc = isLogin(browser,myAccount.fbid)
    if loginSuc:
        logHelper.getLogger().info("login successfuly!")
        #saveCookie(browser, cookieFile)
    else:
        logHelper.getLogger().info("failed in login!")

    return  loginSuc

# '''
# 通过facebook主页登录
# '''
def login_by_up_Homepage(browser,myAccount,cookieFile):
    logInEle = {}
    logInEle['uStr'] = r'//input[@id="email"]'
    logInEle['pStr'] = r'//input[@id="pass"]'
    #  有时候 提交button 的 为  id = "u_0_t"
    logInEle['lStr'] = r'//label[@id="loginbutton"]/input[@type="submit"]'
    return  login_by_up(browser,myAccount,cookieFile,logInEle)

# '''
# 在用户主页采用用户密码方式登录，nickName 登录用户的昵称可以帮助判断是否登录成功
# 返回登录是否成功！
# '''
def login_by_up_userpage(browser, myAccount,cookieFile):
    cur_url = browser.current_url
    logHelper.getLogger().info('login_url: ' + browser.current_url)
    logInEle = {}
    logInEle['uStr'] = r'//input[@id="email"]'
    logInEle['pStr'] = r'//input[@id="pass"]'
    logInEle['lStr'] = r'//label[@id="loginbutton"]/input[@id="u_0_0"]'
    login_by_up(browser,myAccount,cookieFile,logInEle)
    # 返回到登录前页面。
    browser.get(cur_url)
    time.sleep(random.randint(1,4))

def saveCookie(browser, cookieFile):
    myCookie = browser.get_cookies()
    for tmpCookie in myCookie:
        logHelper.getLogger().info(tmpCookie["name"] + ":" + tmpCookie["value"])
    myCookieStr = json.dumps(myCookie)
    with open(cookieFile, 'w') as f:
        f.write(myCookieStr)
    logHelper.getLogger().info("Cookie is saved into file: " + cookieFile + " successfully !")

def executeLogin(user_input, user,pwd_input, pwd, sub_btn):
    user_input.clear()
    user_input.send_keys(user)
    pwd_input.clear()
    pwd_input.send_keys(pwd)
    sub_btn.click()
    time.sleep(random.randint(1,6))

def findLoginInput(browser,uStr,pStr,lStr):
    user_input = FBHelper.find_element(browser, uStr, \
                                       "user input element can not be found")
    pwd_input = FBHelper.find_element(browser, pStr, \
                                      "password input element can not be found")
    sub_btn = FBHelper.find_element(browser, lStr, \
                                    "submit button element can not be found")
    return user_input, pwd_input, sub_btn

def openPhantomJS():
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
    # 不载入图片，爬页面速度会快很多
    # dcap["phantomjs.page.settings.loadImages"] = False
    browser = webdriver.PhantomJS(desired_capabilities=dcap)
    return browser

# '''
# Cookie方式登录，nickName 登录用户的昵称可以帮助判断是否登录成功
# 返回登录是否成功！
# '''
def login_by_cookie(browser,cookieFile,fbid):
    # browser = openPhantomJS()
    # browser = webdriver.Firefox()
    logHelper.getLogger().info('login_url: ' + browser.current_url)
    browser.delete_all_cookies()
    with open(cookieFile, 'r', encoding='utf-8') as f:
        listCookies = json.loads(f.read())

    for tmpCookie in listCookies:
        browser.add_cookie({'domain': '.facebook.com',\
                            'name':tmpCookie["name"],\
                           'value':tmpCookie["value"],\
                            'path': '/',\
                            'expires': None,\
                            })

    if FBHelper.openUrl(browser,browser.current_url):
        # browser()
        # browser.refresh()
        time.sleep(random.randint(1,6))
        loginSuc = isLogin(browser, fbid)

        if loginSuc:
            logHelper.getLogger().info("login by cookie successfuly!")
        else:
            logHelper.getLogger().info("failed in login by cookie!")

        return  loginSuc
    else:
        return  False

# '''
# 判断登录是否成功
# '''
def isLogin(browser, fbid):
    # print(browser.page_source)
    #### 需要跳转确认
    # if browser.page_source.find('Log In With One Tap')>=0:
    #     btn = browser.find_element_by_xpath(r'//button[@class="_54k8 _52jh _56bs _56b_ _56bw _56bu"]')
    #     btn.click()
    #     # print(browser.page_source)
    #     time.sleep(random.randint(1, 6))

    loginSuc = False

    warningStr = "Can not find the fbID element"
    fbidEle = FBHelper.find_element(browser, '//*[contains(@id,"%s")]' % fbid, warningStr)
    if fbidEle is not None:
        loginSuc = True
    else:
        loginSuc = False

    return loginSuc

    #
    # warningStr = "Can not find the nickName element"
    # nickNameEle = FBHelper.find_element(browser, '//a[contains(@class,"_2s25")]', warningStr)
    #
    # if nickNameEle is None:
    #     loginSuc = False
    # else:
    #     if nickName is not None:
    #         if nickName == nickNameEle.text:
    #             loginSuc = True
    #         else:
    #             logHelper.getLogger().warning("Do you give the wrong nickName?")
    #             loginSuc =  False
    #     else:
    #         tmpStr = "login element can not be found"
    #         rstLogin = FBHelper.find_element(browser,r'//a[contains(@class,"_2s25")]',tmpStr,"find_elements_by_xpath")
    #         if rstLogin is None:
    #             loginSuc = False
    #         else:
    #             rstTxt = ""
    #             for ele in rstLogin:
    #                 rstTxt += ele.text
    #             if rstTxt.find("Home") > 0 and rstTxt.find("Find Friends") > 0:
    #                 loginSuc = True
    # return loginSuc

    # if nickName == browser.find_element_by_xpath(r'//a[@class="_2s25"]').text:
        # loginSuc = True
    # else:
    #
    #     try:
    #         browser.find_elements_by_xpath(r'//a[@class="_2s25"]')
    #     except NoSuchElementException as  e:
    #         logHelper.getLogger().debug('login element can not be found, please check whether the page is changed!')
    #         # browser.quit()
    #         return False
    #     rstLogin = browser.find_elements_by_xpath(r'//a[@class="_2s25"]')
    #     rstTxt = ""
    #     for ele in rstLogin:
    #         rstTxt += ele.text
    #     if rstTxt.find("Home") > 0 and rstTxt.find("Find Friends") > 0:
    #         loginSuc = True
    # return loginSuc

if __name__== '__main__':
    myargs = {'fName': 'test.log', 'fLevel': logging.DEBUG}
    logger = logHelper.getLogger('myLog', logging.INFO, **myargs)
    logger.info("============================================================")
    LOGIN_URL  = 'https://www.facebook.com/'
    browser = webdriver.Firefox()
    # browser = openPhantomJS()

    FBHelper.openUrl_exit(browser,LOGIN_URL+'100017274727394',5)

    # try:
    #     # browser.get(LOGIN_URL)
    #     browser.get()
    # except WebDriverException as e:
    #     logger.error("the page can not be opened, please check the status of you network!")
    #     browser.quit()


    browser.implicitly_wait(random.randint(2, 6))  # 随机等待

    myAccount = OurFBAccount('trumpJACK2018@outlook.com', '1qaz@WSX3edc', 'Jack')

    # login_by_up_Homepage(browser,myAccount,'FBCookie.txt')
    # login_by_up_userpage(browser,myAccount,'FBCookie.txt')
    login_by_cookie(browser,'FBCookie.txt',myAccount.fbid)
    browser.quit()


