import pyodbc

_driver = 'SQL Server Native Client 10.0'
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
    
    #表，数据
    def insert(self,table,str):
        conn = pyodbc.connect(driver=_driver, server=_server, user=_user, password=_password, database=_database)
        cur = conn.cursor()
        words = self.select(table)
        #print(words)
        wlist = words
        for i in range(0,len(words)):
            wlist[i] = ''.join(words[i])
        #print(wlist)
        if str in wlist:
            print('无法添加重复屏蔽词')
        else:
            print("可以添加")
            sql = "insert into %s"%table + " values('%s')"%str
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