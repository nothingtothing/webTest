#by 龙波
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

def testModelBySame(testFilePath):
    #读取存储下来的训练训练模型
    transformer_model = joblib.load("../data/result_save_TFM_try")
    svd_model = joblib.load("../data/result_save_SVDM_try")
    model = joblib.load("../data/result_save_AdaBoost_try")
    #预处理数据
    df = pd.read_csv(testFilePath,names = ['frome','to','title','content','classes'] ,encoding="utf-8",sep=",")
    jieba_cut_content = list(df["content"].astype("str"))
    jieba_cut_content = [jiebaclearText(line) for line in jieba_cut_content]
    data_test = pd.DataFrame(svd_model.transform(transformer_model.transform(jieba_cut_content)))
    #进行判断
    y_predict = model.predict(data_test)
    resultList =  list(y_predict)
    #返回结果的数组
    resultList =  [int(i) for i in resultList]
    df['classes'] = resultList
    return df

