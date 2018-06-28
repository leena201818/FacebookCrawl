# encoding=utf-8
from datetime import datetime
import time
import sys
import logging,sys
import common
from SqlServer import *
from queue import PriorityQueue
from loghelper.loghelper import logHelper

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                     datefmt='%Y %b %d %H:%M:%S',
#                     #filename='myapp.log',
#                     #filemode='w',
#                     stream=sys.stdout)

class FBGroupHelper:
    def __init__(self):
        serverconfig = common.getDatabaseServerConfig()
        self.dbinstance = SqlServer(serverconfig[0],serverconfig[1],serverconfig[2],serverconfig[3])

    def ImportFBGroupSeed(self, seedtxtfile, origin):
        with open(seedtxtfile, 'r',encoding='UTF-8') as f:
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                acount = line.split(',')
                fbid = acount[0]
                name = acount[1]
                sql = "insert into tb_seed_group(fbid,name,origin,publishedtime,hasTasked) values(%d,%s,%s,%s,0);"
                param = (fbid, name, origin, now)
                self.dbinstance.ExecNonQuery(sql, param)
                logHelper.getLogger().info("insert {0}".format(line))

    def GenerateGroupTask(self,tasktype):
        '''
        从种子生成任务，按照任务类型，将所有未运行种子都导入
        :param tasktype:
        :return:
        '''
        sql = "insert into tb_task_group(fbid,tasktype,priority,runningstate,deep,name) select fbid,%s,100,0,0,name from tb_seed_group where hastasked = 0;update tb_seed_group set hasTasked = 1,taskedTime=GETDATE() where hastasked = 0"
        logHelper.getLogger().debug(sql)
        param = (tasktype)
        c = self.dbinstance.ExecNonQuery(sql,param)
        logHelper.getLogger().debug('Generate Group Task From Seed is OK!')
        return c

    def LoadTopNTask(self,n,tasktype):
        que = PriorityQueue()
        query = "SELECT TOP {0} id,priority,fbid,originalfbid,deep,name  FROM tb_task_group  WHERE runningState=0 and Tasktype = '{1}' order by priority DESC".format(n,tasktype)
        rows,c = self.dbinstance.ExecQuery(query)

        for row in rows:
            originfbid = row[3]
            deep = row[4]
            name = row[5]
            if row[3] is None:
                originfbid = ''
            if row[4] is None:
                deep = '3'
            if row[5] is None:
                name = ''

            r = common.FBTask(row[0],row[1],row[2],tasktype,originfbid,int(deep),name) #def __init__(self,id,priority,fbid,tasktype,originalfbid,deep,name):
            for i in range(5):
                logHelper.getLogger().debug(row[i])
            tup = (row[1],r)   #priority作为优先级
            que.put(tup)

        return que

    def SetRuningState(self,id,state):
        sql = 'UPDATE tb_task_group SET runningState = %d WHERE id=%d'
        param = (state,id)
        self.dbinstance.ExecNonQuery(sql,param)

    def SetCompleteState(self,id,runningState,desc):
        sql = "UPDATE tb_task_group SET runningState = %d,completedTime = GETDATE(),Description = %s WHERE id=%d"
        param = (runningState,desc,id)
        logHelper.getLogger().debug(sql)
        self.dbinstance.ExecNonQuery(sql,param)

    # 保存关系，传入一个字典
    def Save_tb_group_relationship(self,dicResult):
        #dicResult={'fbida':'111','fbidb':'222','relationtype':'friend'}
        sql = "\
                    IF NOT EXISTS(SELECT * FROM tb_user_relationship WHERE fbida = %d AND fbidb = %d AND relationtype = %s) \
                BEGIN\
                    insert into tb_user_relationship(fbida,fbidb,namea,nameb,relationtype,crawledTime,relationclass) VALUES\
                    (%d,%d,%s,%s,%s,GETDATE(),%s)\
                END"
        # sql = sql.format(fbida=dicResult['fbida'],fbidb=dicResult['fbidb'],relationtype=dicResult['relationtype'])
        param = (dicResult['fbida'], dicResult['fbidb'], dicResult['relationtype'],dicResult['fbida'], dicResult['fbidb'],
                 dicResult['namea'],dicResult['nameb'],dicResult['relationtype'],'GroupMember')
        logHelper.getLogger().debug(sql)
        self.dbinstance.ExecNonQuery(sql,param)

     # 保存timeline，传入一个字典,字段为空，传入None有问题，字符串可''，时间不要insert这个字段就行
    def Save_tb_user_timeline(self,dicResult):
        sql = "\
                IF NOT EXISTS(SELECT * FROM tb_user_timeline WHERE TimelineFBID = %s) \
            BEGIN\
        	    insert into tb_user_timeline(\
        	    TimelineFBID,postUserFBID,postUserName,postTime,content,picturesURLs,\
        	    DZanCount,\
        	    landMarkID,landMarkName,timestamp,crawledTime)\
        	    VALUES(%s,%d,%s,%s,%s,%s,\
        	    %d,%s,%s,%d,GETDATE())\
            END"
        # sql = sql.format(TimelineFBID=dicResult['TimelineFBID'],
        #                  postUserFBID=dicResult['postUserFBID'],
        #                  postUserName=dicResult['postUserName'],
        #                  postTime=dicResult['postTime'],
        #                  content=dicResult['content'],
        #                  picturesURLs=dicResult['picturesURLs'],
        #                  DZanCount=dicResult['DZanCount'],
        #                  landMarkID=dicResult['landMarkID'],
        #                  landMarkName=dicResult['landMarkName'],
        #                  timestamp=dicResult['timestamp']
        #                  )
        logHelper.getLogger().debug(sql)
        # print(dicResult)
        # logHelper.getLogger().debug(dicResult)
        param = (dicResult['TimelineFBID'],
                 dicResult['TimelineFBID'],dicResult['postUserFBID'],dicResult['postUserName'],dicResult['postTime'],dicResult['content'],dicResult['picturesURLs'],
                 dicResult['DZanCount'],
                 dicResult['landMarkID'],dicResult['landMarkName'],dicResult['timestamp'])
        self.dbinstance.ExecNonQuery(sql,param)

    def GenerateUserTaskFromFriends(self,tasktype,whereclause):
        '''
        从朋友生成任务，按照任务类型
        :param tasktype:
        :return:
        '''
        sql = "insert into tb_task_group(fbid,tasktype,priority,runningstate,deep,name) \
                select fbid,%s,priority,0,deep,name from tb_user_friends {0} ; \
                update tb_user_friends set hasTasked = 1,taskedTime=GETDATE() {0}".format(whereclause)
        logHelper.getLogger().debug(sql)
        param = (tasktype)
        c = self.dbinstance.ExecNonQuery(sql,param)
        logHelper.getLogger().debug('Generate {0} User Task from Friends is OK!'.format(c))
        return c

    def UpdateTaskDispatch(self,taskid,spider = ''):
        '''
        分配任务后，填写分配时间
        :param taskid:
        :return:
        '''
        sql = "update tb_task_group set dispatchTime = GETDATE(),Spider = %s where id = %d"
        logHelper.getLogger().debug(sql)
        param = (spider,taskid)
        c = self.dbinstance.ExecNonQuery(sql,param)
        logHelper.getLogger().debug('Update User Task DispatchTime is OK!')
        return c

def main():

    if sys.argv.__len__() != 3:
        print('usage:python importfbcheckseed.py filepath origin')
        exit(1)
    logHelper.getLogger().info(sys.argv[1])
    logHelper.getLogger().info(sys.argv[2])
    seedfile = sys.argv[1]
    origin = sys.argv[2]
    fbhelper = FBUserHelper()
    fbhelper.ImportFBUserSeed(seedfile,origin)
    logHelper.getLogger().info("seed import completed!")

if __name__ == '__main__':

    dicResult = {'fbid': '001',
             'Name': '111',
             'rank': '3'
             }
    FBUserHelper().Save_tb_user_info(dicResult)




