#by 李星星

import pyodbc

_driver = 'ODBC Driver 17 for SQL Server'
_server = 'wkfgdbservice.chinanorth.cloudapp.chinacloudapi.cn,1433'  
_user = 'sa'
_password = 'rootL123456789'
_database = 'test'
    
class DBac:
    
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    #表
    def select(self,tab):
        conn = pyodbc.connect(driver=_driver, server=_server, user=_user, password=_password, database=_database)
        cur = conn.cursor()
        sql = "select * from %s"%tab
        try:
            cur.execute(sql)
        except:
            print("请检查sql语句是否正确")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows   #list
    
    #将邮件插入数据库
    def insertEmail(self,strFrom,strTo,strTitle,strText,intT):
        conn = pyodbc.connect(driver=_driver, server=_server, user=_user, password=_password, database=_database)
        cur = conn.cursor()
        sql = "insert into Emails([from],[to],title,content,type) values('%s','%s','%s','%s','%d')"%(strFrom,strTo,strTitle,strText,intT)
        try:
            cur.execute(sql)
        except:
            print("请检查sql语句是否正确")
        conn.commit()
        cur.close()
        conn.close()

    #将邮件插入数据库
    def insertEmailTest(self,I,F,T,TI,CON,TY,B,CHTML,ATTACH):
        conn = pyodbc.connect(driver=_driver, server=_server, user=_user, password=_password, database=_database)
        cur = conn.cursor()
        sql = "insert into emailTest values('%d','%s','%s','%s','%s','%d','%s','%s','%s')"%(I,F,T,TI,CON,TY,B,CHTML,ATTACH)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

    #获取表中邮件最大ID
    def selectID(self):
        conn = pyodbc.connect(driver=_driver, server=_server, user=_user, password=_password, database=_database)
        cur = conn.cursor()
        sql = "select MAX(ID) from emailTest"
        try:
            cur.execute(sql)
        except:
            print("请检查sql语句是否正确")
        maxID = cur.fetchone()
        cur.close()
        conn.close()
        return maxID[0]

    def insertUser(self,US,mail,Pw):
        conn = pyodbc.connect(driver=_driver, server=_server, user=_user, password=_password, database=_database)
        cur = conn.cursor()
        sql = "insert into User(name,Mail,PassWord) values('%s','%s','%s')"%(US,mail,Pw)
        try:
            cur.execute(sql)
        except:
            print("请检查sql语句是否正确")
        conn.commit()
        cur.close()
        conn.close()

    #向表中插入数据,(表名，列名，插入数据)
    def insert(self,table,lie,str):
        conn = pyodbc.connect(driver=_driver, server=_server, user=_user, password=_password, database=_database)
        cur = conn.cursor()
        words = self.select(table)
        wlist = words
        for i in range(0,len(words)):
            wlist[i] = ''.join(words[i][0])
        if str in wlist:
            print('无法添加重复屏蔽词')
        else:
            print("可以添加")
            sql = "insert into %s(%s) values('%s')"%(table,lie,str)
            try:
                cur.execute(sql)
            except:
                print("请检查sql语句是否正确")
            conn.commit()
        cur.close()
        conn.close()

    #从表中删除
    def delete(self,table,lie,str):
        conn = pyodbc.connect(driver=_driver, server=_server, user=_user, password=_password, database=_database)
        cur = conn.cursor()
        sql = "delete from %s"%table + " where %s"%lie +" = '%s'"%str
        try:
            cur.execute(sql)
        except:
            print("请检查sql语句是否正确")
        conn.commit()
        cur.close()
        conn.close()

    #从表中删除
    def deleteMail(self,I):
        conn = pyodbc.connect(driver=_driver, server=_server, user=_user, password=_password, database=_database)
        cur = conn.cursor()
        sql = "delete from emailTest where ID = '%d'"%I
        try:
            cur.execute(sql)
        except:
            print("请检查sql语句是否正确")
        conn.commit()
        sql1 = "update emailTest set ID = ID - 1  where ID > %d"%I
        cur.execute(sql1)
        conn.commit()
        cur.close()
        conn.close()

    #更新
    def update(self,table,lie,oldStr,newStr):
        self.insert(table,newStrtr)
        self.delete(table,lie,oldStr)

