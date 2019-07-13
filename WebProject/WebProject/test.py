# -*- coding: utf-8 -*
#by 张家楠
from sklearn.externals import joblib
import pandas as pd
import time
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.decomposition import TruncatedSVD  
from sklearn.naive_bayes import BernoulliNB     
from sklearn.metrics import f1_score,precision_score,recall_score
from chineseYeahYeah import jiebaclearText
import pyodbc
import poplib
import html
import DBaction



def getConnection():#连接数据库
    driver = 'ODBC Driver 17 for SQL Server'  
    server = 'wkfgdbservice.chinanorth.cloudapp.chinacloudapi.cn,1433'  
    user = 'sa'
    password = ''
    database = 'test'
    try:
        conn = pyodbc.connect(driver=driver, server=server, user=user, password=password, database=database)
    except Exception as e:
        print("数据库连接失败",e)
    return(conn)

def getFocusname(): #从数据库中获取信息
    conn = getConnection()
    sql = 'select focusname from Focusnames' 
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    focusname=str(rows)
    index = len(rows)
    for i in range(0,index):
        rows[i] = ''.join(rows[i])
    focus_name = rows
    return focus_name

def getWhitelist():#从数据库中获取白名单信息
    conn=getConnection()
    cur = conn.cursor()
    sql = 'select name from Whitelist'  # 查询语句
    try:
        cur.execute(sql)
        rows = cur.fetchall()# list
        whitelist=str(rows)
        index = len(rows)
        for i in range(0,index):
            rows[i] = ''.join(rows[i])
        white_list = rows
    except Exception as e:
        print("请检查sql命令与数据库是否对应",e)
    return white_list

def getBlockedWords():#从数据库中获取黑名单、屏蔽词信息
    conn=getConnection()
    cur = conn.cursor()
    sql = 'select words from BadWords'  
    try:
        cur.execute(sql)
        rows = cur.fetchall()# list
        blockwords=str(rows)
        index = len(rows)
        for i in range(0,index):
            rows[i] = ''.join(rows[i])
    except Exception as e:
        print("请检查sql命令与数据库是否对应",e)
    words_blocklist = rows

    sql1 = 'select blackMail from BadNames'  
    cur1 = conn.cursor()
    try:
        cur1.execute(sql1)
        rows1 = cur1.fetchall()# list
        blockfrom=str(rows1)
        index1 = len(rows1)
        for i in range(0,index1):
            rows1[i] = ''.join(rows1[i])
    except Exception as e:
        print("请检查sql命令与数据库是否对应",e)
    from_blocklist = rows1
    return words_blocklist,from_blocklist

def getMails(): #从数据库中获取邮件信息
    conn = getConnection()
    sql2 = 'select * from emailTest' 
    try:
        df = pd.read_sql(sql2, conn)
    except Exception as e:
        print("请检查sql命令与数据库是否对应",e)
    return df

def testModelBySame(blockwordsList,blockfromList):   #判断是否为垃圾邮件
    words_blocklist,from_blocklist=getBlockedWords()
    white_list=getWhitelist()
    df=getMails()
    dfForEvaluate = df[df['type']==2]   #获取待分类邮件信息，以pandas表格存储
    dfSafe = df[df['type']==0]  #含附件的邮件默认为正常邮件
    wordsStr = list(dfForEvaluate["content"].astype("str"))
    fromStr = list(dfForEvaluate["from"].astype("str")) 
    titleStr =  list(dfForEvaluate["title"].astype("str"))
    i=-1    #记录读取的序号
    for myword in fromStr:  #如在白名单中，直接判为正常邮件。在黑名单中，直接判为垃圾邮件。
        i=i+1
        for word in myword.strip().split(","):
            if(word in white_list):
                dfForEvaluate.ix[i,'blocked']=0
                dfForEvaluate.ix[i,'type']=0
            elif(word in from_blocklist):
                dfForEvaluate.ix[i,'blocked']=1
                dfForEvaluate.ix[i,'type']=1
            else:
                dfForEvaluate.ix[i,'blocked']=2
   

    j=-1    #记录读取的序号
    for myword2 in titleStr:    #如果标题中存在屏蔽词，直接判为垃圾邮件
            j=j+1
            for eachword1 in words_blocklist:
                if(myword2.find(eachword1)!=-1):
                    dfForEvaluate.ix[j,'blocked']=1
                    dfForEvaluate.ix[j,'type']=1
           

    k=-1
    for myword1 in wordsStr:    #如果内容中存在屏蔽词，直接判为垃圾邮件
            k=k+1
            for eachword in words_blocklist:
                if(myword1.find(eachword)!=-1):
                    dfForEvaluate.ix[k,'blocked']=1
                    dfForEvaluate.ix[k,'type']=1
              
                        
    dfBlocked = dfForEvaluate[dfForEvaluate['blocked'] == 1]    #被屏蔽的邮件
    dfWhitelist = dfForEvaluate[dfForEvaluate['blocked'] == 0]  #白名单邮件
    dfLeft = dfForEvaluate[dfForEvaluate['blocked'] ==2]        #除以上两者剩余邮件
    transformer_model = joblib.load("../data/result_save_TFM_try")  #载入保存的模型进行预测
    svd_model = joblib.load("../data/result_save_SVDM_try")
    model = joblib.load("../data/result_save_AdaBoost_try")
    jieba_cut_content = list(dfLeft["content"].astype("str"))
    jieba_cut_content = [jiebaclearText(line) for line in jieba_cut_content]
    y_test = dfLeft["type"]
    data_test = pd.DataFrame(svd_model.transform(transformer_model.transform(jieba_cut_content)))
    y_predict = model.predict(data_test)
    resultList =  list(y_predict)   #存放预测结果
    resultList =  [int(i) for i in resultList]  
    dfLeft['type'] = resultList
    return dfWhitelist,dfSafe,dfLeft,dfBlocked

def joint():
    '''
    根据得到的屏蔽邮件、白名单邮件、剩余邮件等
    生成最终的垃圾邮件和正常邮件
    '''

    
    words_blocklist,from_blocklist=getBlockedWords()
    df=getMails()
    dfWhitelist,dfSafe,dfLeft,dfBlocked = testModelBySame(words_blocklist,from_blocklist)
    ham = []
    spam = []
    dfSpam = dfLeft[dfLeft['type'] == 1]
    dfHam = dfLeft[dfLeft['type'] != 1]
    for index, row in dfHam.iterrows():
        dict ={}
        dict['id']=row['ID']
        dict['from']=row['from']   
        dict['to']=row['to']
        dict['title']=row['title']
        dict['content']=row['CHTML']
        dict['type']=(int)(row['type'])
        ham.append(dict)

    for index, row in dfSafe.iterrows():
        dict ={}
        dict['id']=row['ID']
        dict['from']=row['from'] 
        dict['to']=row['to']
        dict['title']=row['title']
        dict['content']=row['CHTML']
        dict['type']=(int)(row['type'])
        ham.append(dict)

    for index, row in dfWhitelist.iterrows():
        dict ={}
        dict['id']=row['ID']
        dict['from']=row['from'] 
        dict['to']=row['to']
        dict['title']=row['title']
        dict['content']=row['CHTML']
        dict['type']=(int)(row['type'])
        ham.append(dict)


    for  index, row in dfSpam.iterrows():
        dict ={}
        dict['id']=row['ID']
        dict['from']=row['from'] 
        dict['to']=row['to']
        dict['title']=row['title']
        dict['content']=row['CHTML']
        dict['type']=(int)(row['type'])
        spam.append(dict)

    for  index, row in dfBlocked.iterrows():
        dict ={}
        dict['id']=row['ID']
        dict['from']=row['from'] 
        dict['to']=row['to']
        dict['title']=row['title']
        dict['content']=row['CHTML']
        dict['type']=(int)(row['type'])
        spam.append(dict)
    return(ham,spam)