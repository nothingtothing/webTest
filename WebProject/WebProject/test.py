# -*- coding: utf-8 -*
from sklearn.externals import joblib
import pandas as pd
import time
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.decomposition import TruncatedSVD  #降维
from sklearn.naive_bayes import BernoulliNB     #伯努利分布的贝叶斯公式
from sklearn.metrics import f1_score,precision_score,recall_score
from chineseYeahYeah import jiebaclearText
import pyodbc


def getConnection():
    driver = 'SQL Server Native Client 10.0'  # 因版本不同而异
    server = 'wkfgdbservice.chinanorth.cloudapp.chinacloudapi.cn,1433'  
    user = 'sa'
    password = 'rootL123456789'
    database = 'test'
    conn = pyodbc.connect(driver=driver, server=server, user=user, password=password, database=database)
    return(conn)

def getWhitelist():
    conn=getConnection()
    cur = conn.cursor()
    sql = 'select * from Whitelist'  # 查询语句
    cur.execute(sql)
    rows = cur.fetchall()# list
    whitelist=str(rows)
    index = len(rows)
    for i in range(0,index):
        rows[i] = ''.join(rows[i])
    white_list = rows
    return white_list

def getBlockedWords():
    conn=getConnection()
    cur = conn.cursor()
    sql = 'select * from BadWords'  # 查询语句
    cur.execute(sql)
    rows = cur.fetchall()# list
    blockwords=str(rows)
    index = len(rows)
    for i in range(0,index):
        rows[i] = ''.join(rows[i])
    words_blocklist = rows

    sql1 = 'select * from BadNames'  # 查询语句
    cur1 = conn.cursor()
    cur1.execute(sql1)
    rows1 = cur1.fetchall()# list
    blockfrom=str(rows1)
    index1 = len(rows1)
    for i in range(0,index1):
        rows1[i] = ''.join(rows1[i])
    from_blocklist = rows1
    return words_blocklist,from_blocklist

def getMails():
    conn = getConnection()
    sql2 = 'select * from emailTest'  # 查询语句
    #cur2 = conn.cursor()
    #cur2.execute(sql2)
    df = pd.read_sql(sql2, conn)
   # print(df)
    #rows2 = cur2.fetchall()# list
    #blockfrom=str(rows2)
    #index2 = len(rows2)
    #for i in range(0,index2):
    #ows2[i] = ''.join(rows2[i]
    return df

def testModelBySame(blockwordsList,blockfromList): #判断是否为垃圾邮件
    words_blocklist,from_blocklist=getBlockedWords()
    white_list=getWhitelist()
    df=getMails()
    dfForEvaluate = df[df['type']==2]
    #print("dfForEvaluate")
    #print(dfForEvaluate)
    dfSafe = df[df['type']==0]
    #print("dfSafe")
    #print(dfSafe)
    wordsStr = list(dfForEvaluate["content"].astype("str"))
    fromStr = list(dfForEvaluate["from"].astype("str")) 
    titleStr =  list(dfForEvaluate["title"].astype("str"))
   # print(titleStr)
    i=-1
    for myword in fromStr:#如在白名单中，直接判为正常邮件。在黑名单中，直接判为垃圾邮件。
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
   

 
    #print(wordsStr)
    j=-1
    for myword2 in titleStr:
            j=j+1
            for eachword1 in words_blocklist:
                if(myword2.find(eachword1)!=-1):
                   # print(myword2)
                    dfForEvaluate.ix[j,'blocked']=1
                    dfForEvaluate.ix[j,'type']=1
           

    k=-1
    for myword1 in wordsStr:
            k=k+1
            for eachword in words_blocklist:
                if(myword1.find(eachword)!=-1):
                   # print(myword1)
                    dfForEvaluate.ix[k,'blocked']=1
                    dfForEvaluate.ix[k,'type']=1
              

    #print(dfForEvaluate)
    dfBlocked = dfForEvaluate[dfForEvaluate['blocked'] == 1]
    dfWhitelist = dfForEvaluate[dfForEvaluate['blocked'] == 0]
    dfLeft = dfForEvaluate[dfForEvaluate['blocked'] ==2]
    transformer_model = joblib.load("../data/result_save_TFM_try")
    svd_model = joblib.load("../data/result_save_SVDM_try")
    model = joblib.load("../data/result_save_AdaBoost_try")
    #print(model)
    jieba_cut_content = list(dfLeft["content"].astype("str"))
    jieba_cut_content = [jiebaclearText(line) for line in jieba_cut_content]
    #print(jieba_cut_content)
    #print(testList)
    y_test = dfLeft["type"]
    data_test = pd.DataFrame(svd_model.transform(transformer_model.transform(jieba_cut_content)))

    y_predict = model.predict(data_test)
    resultList =  list(y_predict)
    resultList =  [int(i) for i in resultList]
    dfLeft['type'] = resultList
    print(resultList)
    return dfWhitelist,dfSafe,dfLeft,dfBlocked


   # print("准确率为:%.5f" % precision_score(y_test,y_predict))
   # print("召回率为:%.5f" % recall_score(y_test,y_predict))
   # print("F1值为:%.5f" % f1_score(y_test,y_predict))
   
#guolv("../data/blockedwords.txt","../data/blockedfrom.txt","../data/half_40")
#testModelBySame(words_blocklist,from_blocklist,"../data/test_half_40")
def joint():
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
    print(ham)
    print('/n')
    print('/n')
    print('/n')
    print('/n')
    print('/n')
    print('/n')
    print('/n')
    #print(spam)
    return(ham,spam)

joint()