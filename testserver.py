#!encoding=utf-8

import os,time

for i in range(100):
    os.popen(r'python.exe D:\FacebookCrawl\fbuserspidertest.py')
    time.sleep(.5)


from SqlServer import SqlServer
def testDatabaseServer():
    '''
    判断是否连接上数据库服务器：
    :return: 'Connected!' or "Disconnected!"
    '''
    try:
        s = SqlServer('192.168.8.138:1433','sa','1qaz@WSX3edc','FBDB_F')
        return s.test()
    except Exception as e:
        return 'Disconnected!'

import FBUserHelper

if __name__ == '__main2__':
    # for i in range(10000):
    #     print(testDatabaseServer())
    #     time.sleep(1)

    for i in range(1000):
        fb = FBUserHelper.FBUserHelper()
        a = fb.LoadTopNTask(10,'Facebook.userInfo')
        print(i,a.qsize())
        time.sleep(1)
