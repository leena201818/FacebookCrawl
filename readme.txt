===============================运行环境================================================
python3.6
    beautifulsoup4 (4.6.0)
    cycler (0.10.0)
    lxml (3.8.0)
    matplotlib (2.0.2)
    numpy (1.13.1)
    olefile (0.44)
    pbr (3.1.1)
    Pillow (4.2.1)
    pip (9.0.1)
    pymssql (2.1.3)
    pyparsing (2.2.0)
    python-dateutil (2.6.1)
    pytz (2017.2)
    selenium (3.4.3)
    setuptools (28.8.0)
    six (1.10.0)
    stevedore (1.25.0)
    utility (1.0)
sqlserver 2008
firefox,ghostdriver
===============================操作流程================================================
1、安装Sqlserver 2008数据库服务器，创建FBDB数据库
2、配置config.txt设置调度服务器和数据库服务器的链接配置信息
3、安装python3.6、firefox等运行环境
4、选择一台服务器运行TaskServer.py
5、手工录入种子用户,一定要采用UTF-8编码保存成.txt，建议采用pycharm或者其他python编辑器录入
6、导入用户信息种子
7、生成任务，采用手工方式
8、选择多台爬虫客户端，配置好config.txt、ourFBAccount.txt后，启动FBUserSpider.py开始爬取
9、生成任务，采用自动方式，也可以启用定时生成任务程序，具体操作参看下面


===============================操作说明================================================
1、如何导入账号检测种子？
    种子保存到txt文件中，一行一个，采用ImportCheckSeed.py模块导入.注意，参数不要加引号
    >python importcheckseed.py d:\phone.txt origin
    origin是数据来源字符串

2、如何开始账号检测？
    1）启动调度服务端：TaskServer.py
    2）启动检测模块：FBCheckSpiderClient.py（暂时弃用）

3、如何配置调度服务器端口？
    config.txt里面配置"serverIP": "192.168.8.206", "serverPort": "8089"，字典形式

4.1、如何导入用户信息检测种子？
    种子保存到txt文件中，一行一个，采用ImportUserSeed.py模块导入.注意，参数不要加引号
    >python importuserseed.py d:\seed.txt origin
    origin是数据来源字符串

4.2、如何导入地标信息检测种子？
    种子保存到txt文件中，一行一个，采用ImportLandmarkSeed.py模块导入.注意，参数不要加引号
    >python importlandmarkseed.py d:\seed_landmark.txt origin
    origin是数据来源字符串,seed.txt文件一行一个检测对象 1264710149,Ashutosh Adhikari，以逗号分开

5.1、如何生成用户检测任务？
    >python generateusertask.py
    按照提示，选择导入方式1：从人工种子导入，2：从扩展朋友导入
    按照提示，选择任务类型，现阶段都选择1
    按照提示，输入tb_user_friends生成任务的where 子句，默认where hasTasked = 0就可以，需要专业人士使用

5.2、如何生成地标检测任务？
    >python generatelandmarktask.py
    按照提示，选择任务类型，现阶段都选择1

6、如何自动生成任务？
    现阶段采用定时方式生成，目的是不要盲目自动生成一堆任务，这个过程用户可以认为选择那些朋友可以进入任务。需要专业人士，了解tb_user_friends
    >python timerjob.py
    可以修改里面的代码，wherecaluse
    这个方法还定时清理一些表格，备份

7、如何自动下载头像？
    >python imghelper.py
    对应配置文件是configimg.txt,可以设置头像文件存放路径，注意必须手工创建，‘\\’分割。

8、如何启动用户基本信息爬虫？
   首先需要配置登录账号，在ourFBAccount.txt中进行配置，尽量填写真实的nickName
   >python FBUserSpider.py


