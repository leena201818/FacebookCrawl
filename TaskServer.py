# encoding=utf-8
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from datetime import datetime
import time
import socketserver
import logging,sys
from queue import PriorityQueue

from SqlServer import *
from common import TaskInfo
import  common,FBCheckHelper,FBUserHelper,FBLandmarkHelper
import threading

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y %b %d %H:%M:%S',
                    #filename='myapp.log',
                    #filemode='w',
                    stream=sys.stdout)

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

mutex = threading.Lock()

class TaskServer:
    def __init__(self):
        self.fbCheckQueue = PriorityQueue()
        self.fbTaskUserQueue = PriorityQueue()
        self.fbTaskLandmarkQueue = PriorityQueue()
        self.serverconfig = common.getDispatchServerConfig()
        self.__serverIP = serverconfig[0]
        self.__serverPort = int(serverconfig[1])
        self.__fbcheckhelper = FBCheckHelper.FBCheckHelper()
        self.__fbuserhelper = FBUserHelper.FBUserHelper()
        self.__fblandmarkhelper = FBLandmarkHelper.FBLandmarkHelper()

    #####################################ExecQuery##################用户信息###################################################################
    def getATaskUser(self,taskType):
        '''
        根据任务类型，从人员任务列表中提取分配一个任务给爬虫
        :param taskType:任务类型
        :return:common.FBTaskUser，FBTaskUser.id=-1，表明没有任务
        '''
        mutex.acquire()
        try:
            #return common.FBTaskUser(-1, 0, '919761698961', '0', '','3')
            if self.fbTaskUserQueue.empty():
                self.fbTaskUserQueue = self.__fbuserhelper.LoadTopNTask(10,taskType)
                logging.debug('reload {0} fbcheck seed!'.format(self.fbTaskUserQueue.qsize()))

            logging.info('count queue has left {0} fbtaskuser seed'.format(self.fbTaskUserQueue.qsize()))

            if not self.fbTaskUserQueue.empty():
                task = self.fbTaskUserQueue.get()[1]
                #XMLRPC传输的long必须改变成string
                task2 = common.FBTask(str(task.id),int(task.priority),str(task.fbid),task.tasktype,task.originalfbid,str(task.deep),task.name)

                logging.info('dispatch fbtaskuser seed:taskid:{0}/priority:{1}/fbid:{2}/name:{3}'.format(task.id,task.priority,task.fbid,task.name))
                #set the running state to 1 running
                self.__fbuserhelper.SetRuningState(task.id,1)
                return task2
            else:
                return common.FBTask(-1,0,'919761698961','0','0','3','name')  #def __init__(self,id,priority,fbid,tasktype,originalfbid,deep,name):
        finally:
            mutex.release()

    def reportFBTaskUserComplete(self,taskid,runningState,completeDescription):
        '''
        报告完成情况
        :param completeDescription:
        :return:
        '''
        mutex.acquire()
        try:
            logging.info('{0},{1},{2}'.format(taskid,runningState,completeDescription))

            self.__fbuserhelper.SetCompleteState(taskid,runningState,completeDescription)
            return 'OK'
        finally:
            mutex.release()

#######################################################账号检测###################################################################
    def getAFBCheckTask(self):
        '''
        根据任务类型，从任务列表中提取分配一个任务给爬虫
        :param taskType:任务类型
        :return:common.FBCheckTodo，如果FBCheckTodo.id=-1，表明没有任务
        '''
        mutex.acquire()
        try:
            if self.fbCheckQueue.empty():
                self.fbCheckQueue = self.__fbcheckhelper.LoadTopNTask(10)
                logging.debug('reload {0} fbcheck seed!'.format(self.fbCheckQueue.qsize()))

            logging.info('count queue has left {0} fbcheck seed'.format(self.fbCheckQueue.qsize()))

            if not self.fbCheckQueue.empty():
                task = self.fbCheckQueue.get()[1]
                logging.debug('dispatch fbcheck seed:{0}/{1}/{2}'.format(task.id,task.mobileoremail,task.origin))
                #set the running state to 1 running
                self.__fbcheckhelper.SetRuningState(task.id,1)
                return task
            else:
                return common.FBCheckTodo(-1,'0','none')
        finally:
            mutex.release()

    def reportFBCheckTaskComplete(self,taskid,runningState,completeDescription):
        '''
        报告完成情况
        :param completeDescription:
        :return:
        '''
        mutex.acquire()
        try:
            self.__fbcheckhelper.SetCompleteState(taskid,runningState,completeDescription)
            return 'OK'
        finally:
            mutex.release()

#####################################ExecQuery##################地标信息###################################################################
    def getATaskLandmark(self, taskType):
        '''
        根据任务类型，从地标任务列表中提取分配一个任务给爬虫
        :param taskType:任务类型
        :return:common.FBTaskUser，FBTaskUser.id=-1，表明没有任务
        '''
        # return common.FBTaskUser(-1, 0, '919761698961', '0', '','3')
        mutex.acquire()
        try:
            logging.debug('reload {0} fblandmark seed!')
            if self.fbTaskLandmarkQueue.empty():
                self.fbTaskLandmarkQueue = self.__fblandmarkhelper.LoadTopNTask(10, taskType)
                logging.debug('reload {0} fblandmark seed!'.format(self.fbTaskLandmarkQueue.qsize()))

            logging.info('count queue has left {0} fblandmark seed'.format(self.fbTaskLandmarkQueue.qsize()))

            if not self.fbTaskLandmarkQueue.empty():
                task = self.fbTaskLandmarkQueue.get()[1]
                # XMLRPC传输的long必须改变成string
                task2 = common.FBTask(str(task.id), int(task.priority), str(task.fbid), task.tasktype,
                                      task.originalfbid, str(task.deep), task.name)

                logging.debug(
                    'dispatch fblandmark seed:taskid:{0}/priority:{1}/fbid:{2}/name:{3}'.format(task.id, task.priority,
                                                                                                task.fbid, task.name))
                # set the running state to 1 running
                self.__fblandmarkhelper.SetRuningState(task.id, 1)
                return task2
            else:
                return common.FBTask(-1, 0, '919761698961', '0', '0', '3',
                                     'name')  # def __init__(self,id,priority,fbid,tasktype,originalfbid,deep,name):
        finally:
            mutex.release()

    def reportFBTaskLandmarkComplete(self, taskid, runningState, completeDescription):
        '''
        报告完成情况
        :param completeDescription:
        :return:
        '''
        mutex.acquire()
        try:
            print('{0},{1},{2}'.format(taskid, runningState, completeDescription))

            self.__fblandmarkhelper.SetCompleteState(taskid, runningState, completeDescription)
            return 'OK'
        finally:
            mutex.release()

##########################################################################################################################

# Create server
#多线程实现
class RPCThreading(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
    pass

serverconfig = common.getDispatchServerConfig()  # 3
serverIP = serverconfig[0]
serverPort = int(serverconfig[1])
with RPCThreading((serverIP,serverPort),requestHandler=RequestHandler) as server:
#with RPCThreading(("localhost", 8089),requestHandler=RequestHandler) as server:
    #Register my function
    # server.register_function(getATask)

    server.register_instance(TaskServer())

    def test():
        return 'Connected!'
    server.register_function(test)

    # Register a function under a different name
    def adder_function(x,y):
        return x + y
    server.register_function(adder_function, 'add')

    # Register an instance; all the methods of the instance are
    # published as XML-RPC methods (in this case, just 'mul').
    class MyFuncs:
        def mul(self, x, y):
            return x * y

    #server.register_instance(MyFuncs())    #只能注册一个对象

    print('listening on ip {0} / port {1}'.format(serverIP, serverPort))
    logging.info('listening on ip {0} / port {1}'.format(serverIP, serverPort))

    # Run the server's main loop
    server.serve_forever()

