# encoding=utf-8
import logging,sys
from FBCheckHelper import  FBCheckHelper
from loghelper.loghelper import logHelper

# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                     datefmt='%Y %b %d %H:%M:%S',
#                     #filename='myapp.log',
#                     #filemode='w',
#                     stream=sys.stdout)
'''
从txt文件中导入邮箱或手机号，一行一个
>python importfbcheckseed.py d:\phone.txt
'''
if __name__ == '__main__':
    if sys.argv.__len__() != 3:
        print('usage:python importfbcheckseed.py filepath origin')
        exit(1)
    logHelper.getLogger().info(sys.argv[1])
    logHelper.getLogger().info(sys.argv[2])
    seedfile = sys.argv[1]
    origin = sys.argv[2]
    fbhelper = FBCheckHelper()
    fbhelper.ImportFBCheckSeed(seedfile,origin)
    logHelper.getLogger().info("seed import completed!")


