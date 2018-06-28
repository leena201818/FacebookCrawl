# coding=utf-8
# '''
# logging 封装类
# '''
import logging, logging.handlers
import time
import os

# loghelper类
class logHelper():
    logger = None
    def __init__(self):
        pass

    # '''
    # # 获取logger
    # **kw 若要同时返回文件日志，传入字典
    # '''
    # 日志级别大小关系为：CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET，
    @staticmethod
    def getLogger(logName='myLog',csLevel=logging.DEBUG ,**kw):
        if logHelper.logger is None:
            logHelper.logger = logging.getLogger(logName)
            # logHelper.logger.setLevel(logging.NOTSET) # 设置为NOTSET 等于是没设置。会继承root 日志的 默认WARNING 设置，切记
            logHelper.logger.setLevel(logging.DEBUG)

            # 再创建一个handler，用于输出到控制台
            ch = logging.StreamHandler()
            ch.setLevel(csLevel)

            # 定义handler的输出格式
            formatter = logging.Formatter('%(asctime)s-%(name)s-%(filename)s[line:%(lineno)d]-%(levelname)s-%(message)s')
            ch.setFormatter(formatter)
            # 给logger添加handler
            logHelper.logger.addHandler(ch)

            if 'fName' in kw.keys():
                if not os.path.exists('log'):
                    os.makedirs('log')
                # 创建一个handler，用于写入日志文件
                # fh = logging.FileHandler(kw['fName'])
                fh = logging.handlers.TimedRotatingFileHandler('log' + os.path.sep + kw['fName'], when='D', interval=1)
                fh.suffix = "%Y-%m-%d.log"
                fh.setLevel(kw.get('fLevel',logging.DEBUG))
                fh.setFormatter(formatter)
                logHelper.logger.addHandler(fh)

        return logHelper.logger

if __name__ == '__main__':
    # mylogger = logHelper.getLogger('xxxx',logging.DEBUG)
    # mylogger.debug(" debug success ")
    #
    #
    mylogger = logHelper.getLogger('yyyy',csLevel = logging.INFO,**{'fName':"yyyy",'fLevel':logging.DEBUG})
    # mylogger.debug(" debug success ")
    # mylogger.info(" info success ")
    # test_TimedRotatingFileHandler()

    # 测试在200s内创建文件多个日志文件
    for i in range(0, 100):
        mylogger.debug("logging.debug")
        mylogger.info("logging.info")
        mylogger.warning("logging.warning")
        mylogger.error("logging.error")

        time.sleep(2)