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
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows   #list

    def insertEmail(self,strFrom,strTo,strTitle,strText,intT):
        conn = pyodbc.connect(driver=_driver, server=_server, user=_user, password=_password, database=_database)
        cur = conn.cursor()
        sql = "insert into Emails([from],[to],title,content,type) values('%s','%s','%s','%s','%d')"%(strFrom,strTo,strTitle,strText,intT)
        cur.execute(sql)
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
            cur.execute(sql)
            conn.commit()
        cur.close()
        conn.close()

    def delete(self,table,lie,str):
        conn = pyodbc.connect(driver=_driver, server=_server, user=_user, password=_password, database=_database)
        cur = conn.cursor()
        sql = "delete from %s"%table + " where %s"%lie +" = '%s'"%str
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

    def update(self,table,lie,oldStr,newStr):
        self.insert(table,newStrtr)
        self.delete(table,lie,oldStr)