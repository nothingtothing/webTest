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

def testModelBySame(testFilePath):
    transformer_model = joblib.load("../data/result_save_TFM_try")
    svd_model = joblib.load("../data/result_save_SVDM_try")
    model = joblib.load("../data/result_save_AdaBoost_try")
    df = pd.read_csv(testFilePath,names = ['frome','to','title','content','classes'] ,encoding="utf-8",sep=",")
    #df.dropna(axis=0,how="any",inplace=True)
    jieba_cut_content = list(df["content"].astype("str"))
    jieba_cut_content = [jiebaclearText(line) for line in jieba_cut_content]
    data_test = pd.DataFrame(svd_model.transform(transformer_model.transform(jieba_cut_content)))
    y_predict = model.predict(data_test)
    resultList =  list(y_predict)
    resultList =  [int(i) for i in resultList]
    df['classes'] = resultList
    return df

#testModelBySame("../data/test_real")
