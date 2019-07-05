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

def testModelBySame(testFilePath):
    model = joblib.load("../data/result_save_bayes")

    df = pd.read_csv(testFilePath,names = ['a','b','c','content','classes'] ,encoding="utf-8",sep=",")
    df.dropna(axis=0,how="any",inplace=True)    #删除表中含有任何NaN的行
    #x_train,x_test,y_train,y_test = train_test_split(df[["content"]],df["classes"],test_size=0.2,random_state=0)

    transformer = TfidfVectorizer(norm="l2",use_idf=True)
    svd = TruncatedSVD(n_components=20)     #奇异值分解，降维
    jieba_cut_content = list(df["content"].astype("str"))
    y_test = df["classes"]
    transformer_model = transformer.fit(jieba_cut_content)
    df1 = transformer_model.transform(jieba_cut_content)
    svd_model = svd.fit(df1)
    df2 = svd_model.transform(df1)
    data_test = pd.DataFrame(df2)

    y_predict = model.predict(data_test)
    print("准确率为:%.5f" % precision_score(y_test,y_predict))
    print("召回率为:%.5f" % recall_score(y_test,y_predict))
    print("F1值为:%.5f" % f1_score(y_test,y_predict))


testModelBySame("../data/result_spam")