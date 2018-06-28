# encoding=utf-8
import urllib.request
import SqlServer,common,json,datetime
import os,logging,time,threading
from loghelper.loghelper import logHelper

class ImgHelper:
    def __init__(self):
        serverconfig = common.getDatabaseServerConfig()
        self.dbinstance = SqlServer.SqlServer(serverconfig[0],serverconfig[1],serverconfig[2],serverconfig[3])
        myargs = {'fName': "UserInfoCrawler", 'fLevel': logging.DEBUG}
        self.logger = logHelper.getLogger('imgLog', logging.INFO, **myargs)

    def downing(self,remoteUrl,localUrl):
        content = urllib.request.urlopen(remoteUrl).read()
        with open(localUrl,'wb') as f:
            f.write(content)

    def __getLastID(self,keyname):
        with open('configimg.txt', 'r') as f:
            x = json.load(f)
            return x[keyname]

    def __setLastID(self,keyname,lastID):
        x = {}
        with open('configimg.txt', 'r') as f:
            x = json.load(f)
            x[keyname] = lastID

        with open('configimg.txt', 'w') as f:
            json.dump(x, f)

    def downlondUserLogo(self,localDictionary):
        lastID = self.__getLastID('lastUserInfoID')
        if not os.path.exists(localDictionary):
            os.mkdir(localDictionary)

        newdir = os.path.join(localDictionary,datetime.datetime.now().strftime('%Y-%m-%d'))
        if not os.path.exists(newdir):
            os.mkdir(newdir)

        self.logger.info('the last userinfo id stored in configimg.txt is {0}'.format(lastID))

        while(True):
            query = "SELECT TOP 2 id,fbid,logoFile FROM tb_user_info  WHERE id > {0} order by id".format(lastID)
            rows,c = self.dbinstance.ExecQuery(query)

            self.logger.info('load {0} logurl from id:{1}'.format(c,lastID))

            if(int(c) == 0):
                self.logger.info('no logurl,sleep 10 seconds and try again...')
                time.sleep(10)
                continue

            for row in rows:
                try:
                    id = row[0]
                    fbid = row[1]
                    logoFile = row[2]
                    if len(logoFile.strip()) == 0:
                        lastID = int(id)
                        self.__setLastID('lastUserTimelineID', lastID)
                        continue
                    localFileUrl = os.path.join(newdir,'{0}.{1}'.format(fbid,'jpg'))
                    self.downing(logoFile,localFileUrl)
                    self.logger.info('download id:{0},file:{1}'.format(id,localFileUrl))
                    lastID = int(id)
                    self.__setLastID('lastUserInfoID',lastID)

                except Exception as e:
                    self.logger.error(e)
                    continue

    def downlondUserTimelinePictures(self,localDictionary):
        lastID = self.__getLastID('lastUserTimelineID')
        if not os.path.exists(localDictionary):
            os.mkdir(localDictionary)

        newdir = os.path.join(localDictionary,datetime.datetime.now().strftime('%Y-%m-%d'))
        if not os.path.exists(newdir):
            os.mkdir(newdir)

        self.logger.info('the lastUserTimelineID id stored in configimg.txt is {0}'.format(lastID))

        while(True):
            query = "SELECT TOP 2 id,TimelineFBID,postUserFBID,picturesURLs FROM tb_user_timeline  WHERE id > {0} order by id".format(lastID)
            rows,c = self.dbinstance.ExecQuery(query)

            self.logger.info('load {0} picturesURLs from id:{1}'.format(c,lastID))

            if(int(c) == 0):
                self.logger.info('no picturesURLs,sleep 10 seconds and try again...')
                time.sleep(10)
                continue

            for row in rows:
                try:
                    id = row[0]
                    timelineFBID = row[1]
                    postUserFBID = row[2]
                    picturesURLs = row[3]
                    if len(picturesURLs.strip()) == 0:
                        lastID = int(id)
                        self.__setLastID('lastUserTimelineID', lastID)
                        continue
                    print(row)
                    for i,rURL in enumerate(picturesURLs.split(';')):
                        print(i,rURL)
                        if(len(rURL) == 0):
                            continue
                        localFileUrl = os.path.join(newdir,'{0}_{1}.{2}'.format(timelineFBID,i+1,'jpg'))
                        self.downing(rURL,localFileUrl)
                        self.logger.info('download id:{0},file:{1}'.format(id,localFileUrl))

                    lastID = int(id)
                    self.__setLastID('lastUserTimelineID',lastID)

                except Exception as e:
                    self.logger.error(e)

                    continue

if __name__ == '__main__':

    userlogpath = r'.\images\userlogo'
    usertimelinepath = r'.\images\usertimeline'
    with open('configimg.txt', 'r') as f:
        x = json.load(f)
        userlogpath = x['UserInfoImgPath']
        usertimelinepath = x['UserTimelineImgPath']

    print(userlogpath)
    print(usertimelinepath)
    if not os.path.exists(userlogpath):
        print("Please create the dictionary: {0}".format(userlogpath))
        exit(1)

    if not os.path.exists(usertimelinepath):
        print("Please create the dictionary: {0}".format(usertimelinepath))
        exit(1)


    import os
    sel = input('What images do you want to download?:{1:user logo; 2:timeline images; 3:both}' + os.linesep)

    if sel == '1':
        t1 = threading.Thread(target=ImgHelper().downlondUserLogo, args=(r'.\images\userlogo',))
        t1.start()
        t1.join()
    elif sel == '2':
        t2 = threading.Thread(target=ImgHelper().downlondUserTimelinePictures, args=(r'.\images\usertimeline',))
        t2.start()
        t2.join()
    elif sel == '3':
        t1 = threading.Thread(target=ImgHelper().downlondUserLogo, args=(r'.\images\userlogo',))
        t2 = threading.Thread(target=ImgHelper().downlondUserTimelinePictures, args=(r'.\images\usertimeline',))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    else:
        t1 = threading.Thread(target=ImgHelper().downlondUserLogo, args=(r'.\img\userlogo',))
        t1.start()
        t1.join()




