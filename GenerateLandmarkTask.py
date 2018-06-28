# encoding=utf-8
import logging,sys
from FBLandmarkHelper import  FBLandmarkHelper
from loghelper.loghelper import logHelper


'''
种子用户生成任务
>python generateusertask.py
'''
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

if __name__ == '__main__':
    import os
    sel = input('Input TaskType:{1:landmarkInfo; 2:landmarkTimeline; 3:landmarkVisited}'+os.linesep)

    tasktype = 'Facebook.landmarkInfo'
    if sel == '1':
        tasktype = 'Facebook.landmarkInfo'
    elif sel == '2':
        tasktype = 'Facebook.landmarkTimeline'
    elif sel == '3':
        tasktype = 'Facebook.landmarkVisited'
    else:
        tasktype = 'Facebook.landmarkInfo'

    fbhelper = FBLandmarkHelper()
    logging.info(sel)
    logging.info(tasktype)

    c = 0
    de = input('Are you sure? Y:yes  N:no '+os.linesep)
    if(de.upper() == 'Y'):
        c = fbhelper.GenerateLandmarkTask(tasktype)
    else:
        # logging.info("no tasks have generated!")
        print("no tasks have generated!")
        exit(0)

    # logging.info("tasks have generated!")
    print("{0} Landmark Tasks from munual seed has been generated!".format(c))



