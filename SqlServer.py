# encoding=utf-8
import pymssql
class SqlServer:
    def __init__(self,host,user,pwd,db):
        self.host = host    #主机名
        self.user = user    #用户名
        self.pwd = pwd      #密码
        self.db = db        #数据库名

    def __GetConnect(self):
        if not self.db:
            raise(NameError,"No database information is set")
        #连接数据库
        self.conn = pymssql.connect(host=self.host,user=self.user,password=self.pwd,database=self.db,charset="utf8")
     
        cur = self.conn.cursor()
        if not cur:
            raise(NameError,"Unable to connect to the database")
        else:
            return cur

    def ExecQuery(self,sql):    #执行查询语句
        cur = self.__GetConnect()
        cur.execute(sql)
        data = cur.fetchall()    #一次获取全部数据
        # row=cur.fetchone()    #一次获取一行数据
        # rows = cur.fetchmany(10)    #获取10行数据

        #查询完毕后必须关闭连接
        self.conn.close()
        return data,cur.rowcount

    # def ExecNonQuery(self,sql): #执行非查询语句
    #     cur = self.__GetConnect()
    #     cur.execute(sql)
    #     self.conn.commit()
    #     self.conn.close()

    def ExecNonQuery(self,sql,params): #执行非查询语句
        cur = self.__GetConnect()
        c = cur.execute(sql,params)
        self.conn.commit()
        self.conn.close()
        return cur.rowcount

    def ExecNonQueryBatch(self,sql,lstParam): #执行非查询语句
        cur = self.__GetConnect()
        for params in lstParam:
            cur.execute(sql,params)
            # print(params)
        self.conn.commit()
        self.conn.close()
        return cur.rowcount


    def test(self): #测试连接
        try:
            cur = self.__GetConnect()
            return 'Connected!'
        except:
            return 'Disconnected!'

def main():
    #使用sa登录，密码为自设sa登录密码
    ss = SqlServer(host="localhost",user="sa",pwd="1qaz@WSX3edc",db="FBDB")
    # sql = "use FBDB;\
    #             IF NOT EXISTS(SELECT * FROM tb_user_info WHERE fbid = ?) \
    #         BEGIN\
    #     	    insert into tb_user_info(\
    #     	    fbid,Name,rank,crawledTime)\
    #     	    VALUES(?,?,?,GETDATE())\
    #         END"

    sql = 'insert into tb_user_info( fbid,Name,rank,crawledTime) VALUES(%d,%s,%d,%s)'
    dicResult = {}
    dicResult['fbid']=101
    dicResult['Name']= "เฉิ่ม' เบ๊อะ. (เฟสสำรองน้ะ.)"
    dicResult['rank'] = 3
    # ss.ExecNonQuery(sql,(dicResult['fbid'],dicResult['Name'],dicResult['rank']))
    ss.ExecNonQuery(sql, (101,dicResult['Name'],3,'2017-08-14 06:19:35.580'))
    print('update ok')

    #
    # data = ss.ExecQuery("SELECT * FROM tb_seedtype")
    # for row in data:
    #     print(row[0], row[1], row[2])
    # try:
    #     #ss.ExecNonQuery("update tb_seedtype set typename='Facebook' where id = 1")
    #     newtypename='aa'
    #     print('update tb_seedtype set typename ="{0}" where id = 2'.format(newtypename))
    #     ss.ExecNonQuery("update tb_seedtype set typename ='{0}' where id = 2".format(newtypename))
    #
    #     print('update ok')
    # except:
    #     print('update error')
    #
    # try:
    #     ss.ExecNonQuery("delete tb_seedtype where id = 1")
    #     print('delete ok')
    #     ss.ExecNonQuery("insert into tb_seedtype(typevalue,typename) values(1,'Facebook')")
    #     print('insert ok')
    # except:
    #     print('insert error')

if __name__ == '__main__':
    main()