from chineseYeahYeah import jiebaclearText
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
from sklearn.externals import joblib

df = pd.read_csv("../data/result_process01",names = ['a','b','c','content','classes'] ,encoding="utf-8",sep=",")
df.dropna(axis=0,how="any",inplace=True)    #删除表中含有任何NaN的行
#2、数据分割
x_train,x_test,y_train,y_test = train_test_split(df[["content"]],df["classes"],test_size=0.1,random_state=0)

print("训练数据集大小:%d" %x_train.shape[0])
print("测试数据集大小:%d" %x_test.shape[0])
#3、开始模型训练
#3.1、特征工程，将文本数据转换为数值型数据
transformer = TfidfVectorizer(norm="l2",use_idf=True)
svd = TruncatedSVD(n_components=20)     #奇异值分解，降维
jieba_cut_content = list(x_train["content"].astype("str"))
transformer_model = transformer.fit(jieba_cut_content)
df1 = transformer_model.transform(jieba_cut_content)
svd_model = svd.fit(df1)
df2 = svd_model.transform(df1)
data = pd.DataFrame(df2)
nb = BernoulliNB(alpha=1.0,binarize=0.0005) #贝叶斯分类模型构建
model = nb.fit(data,y_train)
print(model)

joblib.dump(nb,"../data/result_save_bayes")

jieba_cut_content_test = list(x_test["content"].astype("str"))
data_test = pd.DataFrame(svd_model.transform(transformer_model.transform(jieba_cut_content_test)))
y_predict = model.predict(data_test)
print(y_predict)

print("准确率为:%.5f" % precision_score(y_test,y_predict))
print("召回率为:%.5f" % recall_score(y_test,y_predict))
print("F1值为:%.5f" % f1_score(y_test,y_predict))