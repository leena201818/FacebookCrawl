# encoding=utf-8
import logging,sys
from FBLandmarkHelper import  FBLandmarkHelper
from loghelper.loghelper import logHelper
'''
从txt文件中导入邮箱或手机号，一行一个
>python importfbcheckseed.py d:\phone.txt
'''
if __name__ == '__main__':
    if sys.argv.__len__() != 3:
        print('usage:python importlandmarkseed.py filepath origin')
        exit(1)
    logHelper.getLogger().info(sys.argv[1])
    logHelper.getLogger().info(sys.argv[2])
    seedfile = sys.argv[1]
    origin = sys.argv[2]
    fblandmarkhelper = FBLandmarkHelper()
    c = fblandmarkhelper.ImportFBLandmarkSeed(seedfile,origin)
    logHelper.getLogger().info("Have imported {0} landmark seed!".format(c))


