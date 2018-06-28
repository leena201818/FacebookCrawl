from selenium import webdriver
import random,time,os

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui
from loghelper.loghelper import logHelper

class GoogleTrans():
    # driver = webdriver.PhantomJS()
    driver = webdriver.Firefox()
    # driver.set_page_load_timeout(15)
    result_xp = "//span[@id='result_box']/span"
    source_xp = "//textarea[@id='source']"
    url = "https://translate.google.cn/#auto/zh-CN/"
    initok = False
    driver.implicitly_wait(10)

    def __init__(self):
        pass

    # 一直等待某元素可见，默认超时10秒
    @classmethod
    def is_visible(cls,locator, timeout=10):
        try:
            ui.WebDriverWait(cls.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except TimeoutException:
            return False

    # 一直等待某个元素消失，默认超时10秒
    @classmethod
    def is_not_visible(cls,locator, timeout=10):
        try:
            ui.WebDriverWait(cls.driver, timeout).until_not(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except TimeoutException:
            return False

    @classmethod
    def translate(cls,txt):     #不够稳定，等待时间不可控，2秒可能有些翻译不出来
        txt = txt.strip()
        txt = txt[:5000]
        txtlen = len(txt)
        if txtlen == 0:
            return''

        if not cls.initok:
            try:
                # logHelper.getLogger().debug('trying to open %s'%cls.url)
                cls.driver.get(cls.url)
                # logHelper.getLogger().debug('has opened  %s' % cls.url)
                if cls.is_visible(cls.source_xp):
                    textSource = cls.driver.find_element_by_xpath(cls.source_xp)
                    logHelper.getLogger().debug('the source text element is visible')
                    # textSource.send_keys('1')
                else:
                    cls.initok = False
                    logHelper.getLogger().debug('does not find the source element,return the original text!')
                    return txt
                cls.is_visible(cls.result_xp)
                # if cls.is_visible(cls.result_xp):
                #     logHelper.getLogger().debug('the result text element is visible')
                # else:
                #     cls.initok = False
                #     logHelper.getLogger().debug('does not find the result element,return the original text!')
                #     return txt
                cls.initok = True
            except Exception as e2:
                logHelper.getLogger().error('cannot open the %s,return the original text' % cls.url)
                logHelper.getLogger().error(e2)
                cls.initok = False
                return txt
        try:
            textSource = cls.driver.find_element_by_xpath(cls.source_xp)
            textSource.clear()
            # textSource.send_keys('0')
            # tryTimes = 0
            # while True:#一直扥到结果发生变化
            #     time.sleep(0.5)
            #     tryTimes += 1
            #     retstr = cls.driver.find_element_by_xpath(cls.result_xp).text
            #     if retstr == '0':
            #         logHelper.getLogger().debug('setting the source text to 0 is ok at {0} times!'.format(tryTimes))
            #         break

            textSource.send_keys(txt)
            if txtlen <= 1000:
                time.sleep(2)
            elif txtlen >= 1000:
                time.sleep(4)

            retstr = ''
            result_box_spans = cls.driver.find_elements_by_xpath(cls.result_xp)
            for rb in result_box_spans:
                retstr = retstr + os.linesep + rb.text
            return retstr.strip()
            # tryTimes = 0
            # while True:#一直扥到结果发生变化
            #     time.sleep(4)
            #     retstr = cls.driver.find_element_by_xpath(cls.result_xp).text
            #     if retstr != '0':
            #         logHelper.getLogger().debug('translate and return the result!')
            #         return retstr
            #     tryTimes += 1
            #     if tryTimes > 5:
            #         logHelper.getLogger().debug('try 4 seconds to translate %s and does not work,return the orginal txt!'%txt)
            #         return txt
            #     logHelper.getLogger().debug('try {0} time to translate !'.format(tryTimes))
            #     logHelper.getLogger().debug('get translate result at {0} time: {}'.format(tryTimes,retstr))

        except Exception as e:
            logHelper.getLogger().error(e)
            cls.initok = False
            return txt

    @classmethod
    def translate_2(cls,txt):   #该方法无法识别特殊字符,需要pip install googletrans,可用于翻译规范的文字
        try:
            txt = txt.strip()
            if len(txt) == 0:
                return''
            from googletrans import Translator
            translator = Translator()
            contentZN = translator.translate(txt, dest='zh-CN').text
            return contentZN
        except Exception as e:
            logger.error(e)
            return txt

    @classmethod
    def translate_api(cls,txt):   #该方法必须登录google账号，需要pip install google-cloud-translate==1.2.0,每日限额3000左右？购买方式
        #https://github.com/GoogleCloudPlatform/google-cloud-python
        txt = txt.strip()
        if len(txt) == 0:
            return''

        from google.cloud import translate

        translate_client = translate.Client()
        target = 'zh-CN'
        translation = translate_client.translate(txt,target_language=target)

        contentZN = translation['translatedText']
        return contentZN


if __name__ == '__main__':
    lq = ['인터넷접속 제한 예정일 : 2017-08-25 ','सब्र कर Pagli मुसीबत के दिन गुजर जायेंगे,आज जो मुझे देखके हंसते है , वो कल मुझे देखते रह जायेंगे .','Môřë ťhãñ yesterday.~ğõõď ñïğhť~!']
    # gt = GoogleTrans()
    import logging
    logName = time.strftime('%Y-%m-%d', time.localtime(time.time())) + ".log"
    myargs = {'fName': logName, 'fLevel': logging.DEBUG}
    logger = logHelper.getLogger('myLog', logging.DEBUG, **myargs)

    # for i,querystr in enumerate(lq):
    #     print(querystr)
    #     print( gt.translate(querystr) )


    import  common
    import SqlServer

    serverconfig = common.getDatabaseServerConfig()
    dbinstance = SqlServer.SqlServer(serverconfig[0],serverconfig[1],serverconfig[2],serverconfig[3])

    # query = "select id,content from tb_user_timeline where id > 2643 order by id"
    query = "select id,content from tb_user_timeline where id > 0 order by id"
    rows,c = dbinstance.ExecQuery(query)
    for r in rows:
        id = r[0]
        content = r[1]
        print(id,content)

        if len(content) == 0:
            continue
        contentZN = GoogleTrans.translate(content)
        # contentZN = GoogleTrans.translate_2(content)
        # contentZN = GoogleTrans.translate_api(content)
        print(contentZN)

        sql = 'update tb_user_timeline set contentZHCN = %s where id = %d'
        param = (contentZN,int(id))
        dbinstance.ExecNonQuery(sql,param)


