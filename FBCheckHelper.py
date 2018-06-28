# encoding=utf-8
from datetime import datetime
import time
import sys
import logging,sys
import common
from SqlServer import *
from queue import PriorityQueue

from loghelper.loghelper import logHelper
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                     datefmt='%Y %b %d %H:%M:%S',
#                     #filename='myapp.log',
#                     #filemode='w',
#                     stream=sys.stdout)

class FBCheckHelper:
    def __init__(self):
        serverconfig = common.getDatabaseServerConfig()
        self.dbinstance = SqlServer(serverconfig[0],serverconfig[1],serverconfig[2],serverconfig[3])

    def ImportFBCheckSeed(self,seedtxtfile,origin):
        with open(seedtxtfile,'r') as f:
            for line in f.readlines():
                if len(line.strip()) == 0:
                    continue
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sql = "use FBDB;insert into tb_fbcheck_todo(mobileoremail,publishedtime,runningState,origin) values('{0}','{1}',{2},'{3}');".format(line.strip(),now,0,origin)
                self.dbinstance.ExecNonQuery(sql)
                logHelper.getLogger().info("insert {0}".format(line))

    def LoadTopNTask(self,n):
        que = PriorityQueue()
        query = 'use FBDB;SELECT TOP {0} [id],[mobileoremail],[origin]  FROM [tb_fbcheck_todo]  WHERE [runningState]=0 order by id '.format(n)
        rows = self.dbinstance.ExecQuery(query)

        for row in rows:
            r = common.FBCheckTodo(int(row[0]),row[1],row[2])
            tup = (int(row[0]),r)
            que.put(tup)

        return que

    def SetRuningState(self,id,state):
        sql = 'use FBDB;UPDATE tb_fbcheck_todo SET runningState = {0} WHERE id={1}'.format(state,id)
        self.dbinstance.ExecNonQuery(sql)

    def SetCompleteState(self,id,runningState,desc):
        sql = "use FBDB;UPDATE tb_fbcheck_todo SET runningState = {0},completedTime = GETDATE(),Description = '{1}' WHERE id={2}".format(runningState,desc,id)
        logHelper.getLogger().debug(sql)
        self.dbinstance.ExecNonQuery(sql)

    def SaveResultToDB(self,lstResult):
        sql = "use FBDB;insert into tb_fbcheck_result(mobileoremail,hasRegistered,Fbid,userName,homepage,Logourl,Description,origin) VALUES('{0}',{1},{2},'{3}','{4}','{5}','{6}','{7}')"
        sql = sql.format(lstResult[0],lstResult[1],lstResult[2],lstResult[3],lstResult[4],lstResult[5],lstResult[6],lstResult[7])
        print(sql)
        self.dbinstance.ExecNonQuery(sql)

def main():

    logHelper.getLogger().info(sys.argv[1])
    seedfile = sys.argv[1]
    fbhelper = FBCheckHelper()
    fbhelper.ImportFBCheckSeed(seedfile)
    logHelper.getLogger().info("seed import completed!")

# if __name__ == '__main__':
#     main()

    # lstResult = ('1', 1, 1, 'name', 'homepage', 'log', '')
    # FBCheckHelper().SaveResultToDB(lstResult)
    #
    # # for i in range(1):
    # #     lstResult=('1',1,1,'name','homepage','log','desc')
    # #     FBCheckHelper().SaveResultToDB(lstResult)
    #
    #
    # que = FBCheckHelper().LoadTopNTask(10)
    # while not que.empty():
    #     t = que.get()
    #     print(t[0])
    #     #FBCheckHelper().SetRuningState(t[0],1)
    #     FBCheckHelper().SetCompleteState(t[0],2,'ok')


