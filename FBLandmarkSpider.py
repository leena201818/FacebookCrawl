# encoding=utf-8
import time
import xmlrpc.client
import logging,sys

import common
from common import *
import FBLandmarkHelper
from utility import OurFBAccount
# from utility import FBHelper,FBBaseUser
from loghelper.loghelper import logHelper

#远程服务代理
serverconfig = common.getDispatchServerConfig()  # 3
serProxy = xmlrpc.client.ServerProxy('http://{0}:{1}'.format(serverconfig[0], serverconfig[1]))

def getFBLandmarkTask(tasktype):
   return serProxy.getATaskLandmark(tasktype)
def reportFBTaskLandmarkComplete(taskid,runningState,completeDescription):
   return serProxy.reportFBTaskLandmarkComplete(taskid,runningState,completeDescription)


def main():
    fblandmarkhelper = FBLandmarkHelper.FBLandmarkHelper()
    # # 登录
    # # fbAccount = ourFBAccount('trumpJACK2018@outlook.com', '1qaz@WSX3edc', None)
    # fbAccount = OurFBAccount.getAccount('ourFBAccount.txt')
    # logName = time.strftime('%Y-%m-%d', time.localtime(time.time())) + ".log"
    # myargs = {'fName': logName, 'fLevel': logging.DEBUG}
    # logger = logHelper.getLogger('myLog', logging.INFO, **myargs)
    #
    # # 初始化
    # modify!
    # logger.info("============================================================")
    # # browser, isLogin = FBUserCrawler.initCrawler("https://www.facebook.com/", fbAccount)
    # # if not isLogin:
    # #     logHelper.getLogger().info("login error.please check the log file!")
    # #     time.sleep(10)
    # #     exit(1)

    while True:
        try:
            logHelper.getLogger().info('connecting dispatch server {0}:{1}'.format(serverconfig[0], serverconfig[1]))
            if common.testDispatchServer() == 'Disconnected!':  #1.测试调度服务器连接
                logHelper.getLogger().info('Dispatch server is disconnected!')
                time.sleep(5)
                continue
            logHelper.getLogger().info('Dispatch server is connected!')

            logHelper.getLogger().debug('connecting database server ...')
            if common.testDatabaseServer() == 'Disconnected!':  #2.测试服务器连接
                logHelper.getLogger().info('Database server is disconnected!,trying again later.')
                time.sleep(5)
                continue
            print('Database server is connected!')

            spiderType = 'Facebook.landmarkInfo'    #对应任务类型
            task = getFBLandmarkTask(spiderType)

            taskid = task['id']
            if int(taskid) == -1:
                time.sleep(5)
                continue

            fbid = task['fbid']
            originalfbid = task['originalfbid']
            deep = int(task['deep'])     #当前任务深度，在保存tb_user_friends时+1保存入库
            name = task['name']
            priority = task['priority']

            # fbUser = FBBaseUser(fbid,name,deep,priority)

            # logHelper.getLogger().debug(task)
            logHelper.getLogger().info('Spider [{0}] have got a task:{1}/{2}/{3}. spider is working...'.format(spiderType,taskid,fbid,originalfbid))
            time.sleep(5)
            #开始单线程爬取工作#####################################################################################################
            try:
                # 填写分配任务时间和承担的spider=''
                fblandmarkhelper.UpdateTaskDispatch(int(taskid))

                # modify!
                # if FBLandmarkCrawler.crawleInfo(browser, fbUser, fbAccount) == 1:
                if True:
                    #完成工作,入库
                    print('Spider have done the job. Saving the results...')


                    #告知调度端完成情况
                    print('Spider have saved the results,and reporting the job to dispatch server...')
                    k = reportFBTaskLandmarkComplete(taskid, 2, 'completed normally.')
                    print('task id:{0},fbid:{1} has reported the job status.'.format(taskid,fbid))

            except Exception as e1:
                logHelper.getLogger().error(e1)
                reportFBTaskLandmarkComplete(taskid, 3, 'completed abnormally.Error:{0}'.format(e1))
                #raise  e1

            time.sleep(15)
            # 结束单线程爬取工作#####################################################################################################
        except Exception as e:
            logHelper.getLogger().error(e)
            logHelper.getLogger().error('the main loop error,restart it!')
            time.sleep(50)

if __name__ == '__main__':
    main()

