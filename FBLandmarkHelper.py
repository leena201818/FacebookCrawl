# encoding=utf-8
from datetime import datetime
import time
import sys
import logging,sys
import common
from SqlServer import *
from queue import PriorityQueue
from loghelper.loghelper import logHelper
# from GoogleTrans import *


class FBLandmarkHelper:
    def __init__(self):
        serverconfig = common.getDatabaseServerConfig()
        self.dbinstance = SqlServer(serverconfig[0],serverconfig[1],serverconfig[2],serverconfig[3])

    def ImportFBLandmarkSeed(self, seedtxtfile, origin):
        c = 0
        with open(seedtxtfile, 'r',encoding='UTF-8') as f:
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                acount = line.split(',')
                fbid = acount[0]
                name = acount[1]
                sql = "insert into tb_seed_landmark(fbid,name,origin,publishedtime,hasTasked) values(%d,%s,%s,%s,0);"
                param = (fbid, name, origin, now)
                self.dbinstance.ExecNonQuery(sql, param)
                logHelper.getLogger().info("insert {0}".format(line))
                c = c+1
        return c


    def GenerateLandmarkTask(self,tasktype):
        '''
        从种子生成任务，按照任务类型，将所有未运行种子都导入
        :param tasktype:
        :return:
        '''
        sql = "insert into tb_task_landmark(fbid,tasktype,priority,runningstate,deep,name) select fbid,%s,100,0,0,name from tb_seed_landmark where hastasked = 0;update tb_seed_landmark set hasTasked = 1,taskedTime=GETDATE() where hastasked = 0"
        # logHelper.getLogger().debug(sql)
        param = (tasktype)
        c = self.dbinstance.ExecNonQuery(sql,param)
        logHelper.getLogger().debug('Generate Landmark Task From Seed is OK!')
        return c

    def LoadTopNTask(self,n,tasktype):
        que = PriorityQueue()
        query = "SELECT TOP {0} id,priority,fbid,originalfbid,deep,name  FROM tb_task_landmark  WHERE runningState=0 and Tasktype = '{1}' order by priority DESC".format(n,tasktype)
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
        sql = 'UPDATE tb_task_landmark SET runningState = %d WHERE id=%d'
        param = (state,id)
        self.dbinstance.ExecNonQuery(sql,param)

    def SetCompleteState(self,id,runningState,desc):
        sql = "UPDATE tb_task_landmark SET runningState = %d,completedTime = GETDATE(),Description = %s WHERE id=%d"
        param = (runningState,desc,id)
        logHelper.getLogger().debug(sql)
        self.dbinstance.ExecNonQuery(sql,param)

    # 保存关系，传入一个字典
    def Save_tb_user_relationship(self,dicResult):
        #dicResult={'fbida':'111','fbidb':'222','relationtype':'friend'}
        sql = "\
                    IF NOT EXISTS(SELECT * FROM tb_user_relationship WHERE fbida = %d AND fbidb = %d AND relationtype = %s) \
                BEGIN\
                    insert into tb_user_relationship(fbida,fbidb,namea,nameb,relationtype,crawledTime,relationclass) VALUES\
                    (%d,%d,%s,%s,%s,GETDATE(),%s)\
                END"
        # sql = sql.format(fbida=dicResult['fbida'],fbidb=dicResult['fbidb'],relationtype=dicResult['relationtype'])
        param = (dicResult['fbida'], dicResult['fbidb'], dicResult['relationtype'],dicResult['fbida'], dicResult['fbidb'],
                 dicResult['namea'],dicResult['nameb'],dicResult['relationtype'],'LandmarkVisitor')
        logHelper.getLogger().debug(sql)
        self.dbinstance.ExecNonQuery(sql,param)

    #保存朋友信息，传入一个字典
    def Save_tb_user_friends(self,dicResult):
        # dicResult={'fbid':'111','name':'na','homepage':'','priority':'1','Description':'ddd'}
        sql = "\
                        IF NOT EXISTS(SELECT * FROM tb_user_friends WHERE Fbid = %s) \
                    BEGIN\
                	    insert into tb_user_friends(Fbid,Name,Homepage,priority,crawledTime,hasTasked,deep,Description) VALUES\
                	    (%s,%s,%s,%d,GETDATE(),0,%d,%s)\
                    END"
        # sql = sql.format(fbid=dicResult['fbid'], name=dicResult['name'], homepage=dicResult['homepage'],
        #                  priority=dicResult['priority'], Description=dicResult['Description'])
        dicResult['name'] = dicResult['name'][:120]
        param = (dicResult['fbid'],dicResult['fbid'],dicResult['name'],dicResult['homepage'],dicResult['priority'],dicResult['deep'],dicResult['Description'])
        logHelper.getLogger().debug(sql)
        # print(dicResult)
        # logHelper.getLogger().debug(dicResult)
        self.dbinstance.ExecNonQuery(sql,param)
        # print("ok！")

    # 保存timeline，传入一个字典,字段为空，传入None有问题，字符串可''，时间不要insert这个字段就行
#    modify!
    def Save_tb_landmark_timeline(self,dicResult):
        sql = "\
                IF NOT EXISTS(SELECT * FROM tb_user_timeline WHERE TimelineFBID = %s) \
            BEGIN\
        	    insert into tb_user_timeline(\
        	    TimelineFBID,postUserFBID,postUserName,postTime,content,picturesURLs,picturesAlts,\
        	    DZanCount,\
        	    landMarkID,landMarkName,timestamp,crawledTime,contentZHCN)\
        	    VALUES(%s,%d,%s,%s,%s,%s,%s,\
        	    %d,\
        	    %s,%s,%d,GETDATE(),%s)\
            END"

        logHelper.getLogger().debug(sql)
        # print(dicResult)
        # logHelper.getLogger().debug(dicResult)
        dicResult['postUserName'] = dicResult['postUserName'][:120]
        dicResult['landMarkID'] = dicResult['landMarkID'][:50]
        dicResult['landMarkName'] = dicResult['landMarkName'][:120]

        import  GoogleTrans

        dicResult['contentZHCN'] = GoogleTrans.translate(dicResult['content'])
        dicResult['picturesAlts'] = GoogleTrans.translate(dicResult['picturesAlts'])
        dicResult['picturesAlts'] = dicResult['picturesAlts'][:300]

        param = (dicResult['TimelineFBID'],
                 dicResult['TimelineFBID'],dicResult['postUserFBID'],dicResult['postUserName'],dicResult['postTime'],dicResult['content'],dicResult['picturesURLs'],dicResult['picturesAlts'],
                 dicResult['DZanCount'],
                 dicResult['landMarkID'],dicResult['landMarkName'],dicResult['timestamp'],dicResult['contentZHCN'])
        self.dbinstance.ExecNonQuery(sql,param)

    # 保存landmark_info，传入一个字典,字段为空，传入None有问题，字符串可''，时间不要insert这个字段就行
#    modify!
    def Save_tb_landmark_info(self,dicResult):
        sql = "\
                IF NOT EXISTS(SELECT * FROM tb_user_info WHERE fbid = %d) \
            BEGIN\
        	    insert into tb_user_info(fbid,Name,fbHomepage,logoFile,\
        	    Gender,rank,Birthday,EDU,Work,currentCity,\
        	    homeTown,Languages,homePageUrl,phone,email,interestedIn,favoriteQuotes,\
        	    selfIntro,lifeEvents,Relationship,Description,crawledTime)\
        	    VALUES(%d,%s,%s,%s,%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,GETDATE())\
            END"
        logHelper.getLogger().debug(sql)
        print(dicResult)

        dicResult['Name'] = dicResult['Name'][:120]
        dicResult['fbHomepage'] = dicResult['fbHomepage'][:128]
        dicResult['EDU'] = dicResult['EDU'][:1000]
        dicResult['Work'] = dicResult['Work'][:1000]
        dicResult['currentCity'] = dicResult['currentCity'][:100]
        dicResult['homeTown'] = dicResult['homeTown'][:100]
        dicResult['Languages'] = dicResult['Languages'][:50]
        dicResult['phone'] = dicResult['phone'][:50]
        dicResult['email'] = dicResult['email'][:80]
        dicResult['interestedIn'] = dicResult['interestedIn'][:50]
        dicResult['favoriteQuotes'] = dicResult['favoriteQuotes'][:1000]
        dicResult['selfIntro'] = dicResult['selfIntro'][:500]
        dicResult['lifeEvents'] = dicResult['lifeEvents'][:1000]
        dicResult['Relationship'] = dicResult['Relationship'][:100]

        param = (dicResult['fbid'],dicResult['fbid'],dicResult['Name'],dicResult['fbHomepage'],dicResult['logoFile'],
                 dicResult['Gender'], dicResult['rank'], dicResult['Birthday'], dicResult['EDU'], dicResult['Work'],
                 dicResult['currentCity'], dicResult['homeTown'], dicResult['Languages'], dicResult['homePageUrl'],dicResult['phone'], dicResult['email'],
                 dicResult['interestedIn'], dicResult['favoriteQuotes'], dicResult['selfIntro'], dicResult['lifeEvents'], dicResult['Relationship'],
                 dicResult['Description'],
                 )
        self.dbinstance.ExecNonQuery(sql, param)

    def UpdateTaskDispatch(self,taskid,spider = ''):
        '''
        分配任务后，填写分配时间
        :param taskid:
        :return:
        '''
        sql = "update tb_task_landmark set dispatchTime = GETDATE(),Spider = %s where id = %d"
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
    fbhelper = FBLandmarkHelper()
    fbhelper.ImportFBUserSeed(seedfile,origin)
    logHelper.getLogger().info("seed import completed!")

if __name__ == '__main__':
    FBLandmarkHelper().GenerateUserTask('Facebook.userInfo')



