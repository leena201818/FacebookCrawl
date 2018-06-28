# encoding=utf-8
import json
import xmlrpc.client
from SqlServer import SqlServer
import logging,sys

from loghelper.loghelper import logHelper
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                     datefmt='%Y %b %d %H:%M:%S',
#                     #filename='myapp.log',
#                     #filemode='w',
#                     stream=sys.stdout)

# An arbitrary collection of objects supported by pickle.
# data = {
#     'dbIP':'127.0.0.1',
#     'dbPort':'1433',
# 	'dbUser':'sa',
# 	'dbPwd':'1qaz@WSX3edc',
# 	'dbName':'FacebookDB',
# 	'serverIP':'127.0.0.1',
# 	'serverPort':'8089'
# }
#
# with open('config.txt', 'w') as f:
#     json.dump(data, f)

def getDispatchServerConfig():
    with open('config.txt', 'r') as f:
        x = json.load(f)
        return x['serverIP'], x['serverPort']


def getDatabaseServerConfig():
    with open('config.txt', 'r') as f:
        x = json.load(f)
        return '{0}:{1}'.format(x['dbIP'], x['dbPort']), x['dbUser'], x['dbPwd'], x['dbName']

def testDispatchServer():
    '''
    判断是否连接上调度服务器：
    :return:'Connected!' or "Disconnected!"
    '''
    serverconfig = getDispatchServerConfig()
    try:
        s = xmlrpc.client.ServerProxy('http://{0}:{1}'.format(serverconfig[0], serverconfig[1]))
        logHelper.getLogger().debug('connecting to the dispatch server http://{0}:{1}'.format(serverconfig[0], serverconfig[1]))
        return s.test()
    except Exception as e:
        logHelper.getLogger().error(e)
        return 'Disconnected!'

def testDatabaseServer():
    '''
    判断是否连接上数据库服务器：
    :return: 'Connected!' or "Disconnected!"
    '''
    try:
        serverconfig = getDatabaseServerConfig()
        logHelper.getLogger().debug('connecting to the database server {0}:{1}'.format(serverconfig[0],serverconfig[3]))
        s = SqlServer(serverconfig[0],serverconfig[1],serverconfig[2],serverconfig[3])
        return s.test()
    except Exception as e:
        logHelper.getLogger().error(e)
        return 'Disconnected!'

class TaskInfo:
    '''
    任务基本属性
    taskType：
    {
        Facebook.userInfo:人物信息，包括基本、动态、好友
            Facebook.userBaseinfo:仅人物基本信息
            Facebook.userTimeline: 仅人物动态信息
            Facebook.userFriends: 仅人物好友列表
        Facebook.groupInfo:社团信息
            Facebook.groupTimeLine:仅社团动态信息
            Facebook.groupMembers:仅社团成员列表
        Facebook.landmarkInfo:地标信息
            Facebook.landmarkTimeline:仅地标动态信息
            Facebook.landmarkVisited:仅地标访问者
        Facebook.fbcheck

    }
    '''
    def __init__(self,taskType,taskid,uid,url):
        self.taskType   =   taskType    #爬虫类型，对应任务类型{}
        self.taskid     =   taskid      #唯一ID
        self.uid        =   uid         #账号ID
        self.url        =   url         #账号主页url

'''
    relationship：
    {
        familymember
        friend
        visitor
        member
        follow
    }
'''

class FBCheckTodo():
    '''
    网络上传输的账号检测任务对象
    通过RPC调用变成字典访问
    '''
    def __init__(self,id,mobileoremail,origin):
        self.id = id
        self.mobileoremail = mobileoremail
        self.origin = origin

    def __lt__(self, other):
        if self.id < other.id:
            return 1
        elif self.id == other.id:
            return 0
        else:
            return -1

class FBTask():
    '''
    网络上传输的人员爬取任务对象
    通过RPC调用变成字典访问:item['fbid']
    '''
    def __init__(self,id,priority,fbid,tasktype,originalfbid,deep,name):
        self.id = id
        self.priority = priority
        self.fbid = fbid
        self.tasktype = tasktype
        self.originalfbid = originalfbid
        self.deep = deep
        self.name = name

    def __lt__(self, other):
        if self.priority < other.priority:
            return 1
        elif self.priority == other.priority:
            return 0
        else:
            return -1


