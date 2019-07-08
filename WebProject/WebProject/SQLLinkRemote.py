import pyodbc

driver = 'SQL Server Native Client 11.0'  # 因版本不同而异
server = '42.159.87.121'  
user = 'sa'
password = 'rootL123456789'
database = 'test'
 
conn = pyodbc.connect(driver=driver, server=server, user=user, password=password, database=database)
 
cur = conn.cursor()
sql = 'select * from Persons'  # 查询语句
cur.execute(sql)
rows = cur.fetchall()  # list
print(rows)
conn.close()