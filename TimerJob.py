# encoding=utf-8
from threading import Timer
import FBUserHelper

class MyTimerJob:
    def __init__(self):
        pass

    def printHello(self):
        print("Hello World")
        t = Timer(2, self.printHello)
        t.start()

    def printMe(self):
        print("Hello mmmm")
        t = Timer(2, self.printMe)
        t.start()

    def GenerateTaskFromFriends(self,delayseconds,tasktype,whereclause='where hasTasked = 0'):
        fbhelper = FBUserHelper.FBUserHelper()
        c = fbhelper.GenerateUserTask(tasktype)
        print("{0} User Tasks from munual seed has been generated!".format(c))

        c = fbhelper.GenerateUserTaskFromFriends(tasktype, whereclause)
        print("{0} User Tasks from Friends has been generated!".format(c))

        t = Timer(delayseconds, self.GenerateTaskFromFriends,kwargs={'delayseconds':delayseconds,'tasktype':tasktype,'whereclause':whereclause})
        t.start()

    def Dump2TaskUserLog(self,delayseconds):
        fbhelper = FBUserHelper.FBUserHelper()
        c = fbhelper.DumpTaskUser()
        print('Dump {0} User Task to tb_task_user_log!'.format(c))

        t = Timer(delayseconds, self.Dump2TaskUserLog,kwargs={'delayseconds':delayseconds})
        t.start()

if __name__ == "__main__":
    # printHello()
    # printMe()
    #定时生成任务
    tasktype = 'Facebook.userInfo'
    #whereclause = 'where hasTasked = 0 and id < 210'
    whereclause = 'where hasTasked = 0 and priority >=0'
    MyTimerJob().GenerateTaskFromFriends(60,tasktype,whereclause)

    #定时转出任务
    MyTimerJob().Dump2TaskUserLog(30)