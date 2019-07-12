# -*- coding: utf-8 -*-
#by 龙波、张家楠
import numpy as np
import re
import random
import pandas as pd

from chineseYeahYeah import jiebaclearText



"""
函数说明:将切分的实验样本词条整理成不重复的词条列表，也就是词汇表
Parameters:
    dataSet - 整理的样本数据集
Returns:
    vocabSet - 返回不重复的词条列表，也就是词汇表
"""

def createVocabList(dataSet):
    vocabSet = set([])  # 创建一个空的不重复列表
    for document in dataSet:
        vocabSet = vocabSet | set(document)  # 取并集
    return list(vocabSet)


"""
函数说明:根据vocabList词汇表，将inputSet向量化，向量的每个元素为1或0
Parameters:
    vocabList - createVocabList返回的列表
    inputSet - 切分的词条列表
Returns:
    returnVec - 文档向量,词集模型
"""
def setOfWords2Vec(vocabList, inputSet):
    returnVec = [0] * len(vocabList)               #创建一个其中所含元素都为0的向量
    for word in inputSet:                          #遍历每个词条
        if word in vocabList:                      #如果词条存在于词汇表中，则置1
            returnVec[vocabList.index(word)] = 1
        else:
            print("the word: %s is not in my Vocabulary!" % word)
    return returnVec        #返回文档向量


"""
函数说明:根据vocabList词汇表，构建词袋模型
Parameters:
    vocabList - createVocabList返回的列表
    inputSet - 切分的词条列表
Returns:
    returnVec - 文档向量,词袋模型
"""
def bagOfWords2VecMN(vocabList, inputSet):
    returnVec = [0] * len(vocabList)  # 创建一个其中所含元素都为0的向量
    for word in inputSet:             # 遍历每个词条
        if word in vocabList:         # 如果词条存在于词汇表中，则计数加一
            returnVec[vocabList.index(word)] += 1
    return returnVec  # 返回词袋模型


"""
函数说明:朴素贝叶斯分类器训练函数
Parameters:
    trainMatrix - 训练文档矩阵，即setOfWords2Vec返回的returnVec构成的矩阵
    trainCategory - 训练类别标签向量，即loadDataSet返回的classVec
Returns:
    p0Vect - 正常邮件类的条件概率数组
    p1Vect - 垃圾邮件类的条件概率数组
    pAbusive - 文档属于垃圾邮件类的概率
"""
def trainNB0(trainMatrix, trainCategory):
    numTrainDocs = len(trainMatrix)  # 计算训练的文档数目
    numWords = len(trainMatrix[0])  # 计算每篇文档的词条数
    pAbusive = sum(trainCategory) / float(numTrainDocs)  # 文档属于垃圾邮件类的概率
    p0Num = np.ones(numWords)
    p1Num = np.ones(numWords)  # 创建numpy.ones数组,词条出现数初始化为1,拉普拉斯平滑
    p0Denom = 2.0
    p1Denom = 2.0  # 分母初始化为2 ,拉普拉斯平滑
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:  # 统计属于侮辱类的条件概率所需的数据，即P(w0|1),P(w1|1),P(w2|1)···
            p1Num += trainMatrix[i]
            p1Denom += sum(trainMatrix[i])
        else:  # 统计属于非侮辱类的条件概率所需的数据，即P(w0|0),P(w1|0),P(w2|0)···
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    p1Vect = np.log(p1Num / p1Denom)
    p0Vect = np.log(p0Num / p0Denom)   #取对数，防止下溢出
    return p0Vect, p1Vect, pAbusive  # 返回属于正常邮件类的条件概率数组，属于侮辱垃圾邮件类的条件概率数组，文档属于垃圾邮件类的概率


"""
函数说明:朴素贝叶斯分类器分类函数
Parameters:
	vec2Classify - 待分类的词条数组
	p0Vec - 正常邮件类的条件概率数组
	p1Vec - 垃圾邮件类的条件概率数组
	pClass1 - 文档属于垃圾邮件的概率
Returns:
	0 - 属于正常邮件类
	1 - 属于垃圾邮件类
"""
def classifyNB(vec2Classify, p0Vec, p1Vec, pClass1):
    #p1 = reduce(lambda x, y: x * y, vec2Classify * p1Vec) * pClass1  # 对应元素相乘
    #p0 = reduce(lambda x, y: x * y, vec2Classify * p0Vec) * (1.0 - pClass1)
    p1=sum(vec2Classify*p1Vec)+np.log(pClass1)
    p0=sum(vec2Classify*p0Vec)+np.log(1.0-pClass1)
    if p1 > p0:
        return 1
    else:
        return 0

"""
函数说明:接收一个大字符串并将其解析为字符串列表
"""
def textParse(bigString):  # 将字符串转换为字符列表
    listOfTokens = re.split(r'\W*', bigString)  # 将特殊符号作为切分标志进行字符串切分，即非字母、非数字
    return [tok.lower() for tok in listOfTokens if len(tok) > 2]  # 除了单个字母，例如大写的I，其它单词变成小写


"""
函数说明:测试朴素贝叶斯分类器，使用朴素贝叶斯进行交叉验证
"""

MAX = 0
testSet = []      # 创建存储训练集的索引值的列表和测试集的索引值的列表
testClass = []
vocabList = []

def spamTest():
    docList = []
    classList = []
    fullText = []

    trainingMAX = 200

    global MAX 
    global testSet
    global vocabList
    global testClass

    MAX = 128

    ham_path = "../data/result_ham"
    spam_path = "../data/result_spam"
    flie_path = [ham_path,spam_path]
    for path in flie_path:
        df = pd.read_csv(path,encoding="utf-8",sep=",")
        df.dropna(axis=0,how="any",inplace=True) #出去
        df.columns = ['a','b','c','content','classes']
        print(df.content.ix[129])
        for i in range(0,MAX):
            docList.append(df.content.ix[i].split())
            classList.append(df.classes.ix[i])

    vocabList += createVocabList(docList)
    trainingSet = list(range(0,MAX*2))


    for i in range((int)(MAX * 0.2)):  # 从50个邮件中，随机挑选出40个作为训练集,10个做测试集
        randIndex = int(random.uniform(0, len(trainingSet)))  # 随机选取索索引值
        testSet.append(docList[randIndex])  # 添加测试集的索引值
        testClass.append(classList[randIndex])
        del (trainingSet[randIndex])  # 在训练集列表中删除添加到测试集的索引值

    trainMat = []
    trainClasses = []  # 创建训练集矩阵和训练集类别标签系向量
    for docIndex in trainingSet:  # 遍历训练集
        trainMat.append(setOfWords2Vec(vocabList, docList[docIndex]))  # 将生成的词集模型添加到训练矩阵中
        trainClasses.append(classList[docIndex])  # 将类别添加到训练集类别标签系向量中
    p0V, p1V, pSpam = trainNB0(np.array(trainMat), np.array(trainClasses))  # 训练朴素贝叶斯模型\


    with open("../data/result_save_p0V",'w', encoding='utf-8') as file:
        for index in range(len(p0V)):
            content =str(p0V[index]) + '\n'
            file.writelines(content)

    with open("../data/result_save_p1V",'w', encoding='utf-8') as file:
          for index in range(len(p1V)):
            content =str(p1V[index]) + '\n'
            file.writelines(content)

    with open("../data/result_save_pSpam",'w', encoding='utf-8') as file:
            file.writelines(str(pSpam))

    with open("../data/result_save_vocabList",'w', encoding='utf-8') as file:
        for index in range(len(vocabList)):
             content = vocabList[index] + '\n'
             file.writelines(content)
    return p0V,p1V,pSpam

    #测试代码
def resultTest(p0V,p1V,pSpam):
    errorCount = 0  # 错误分类计数
    for docIndex in range(len(testSet)):  # 遍历测试集
        wordVector = setOfWords2Vec(vocabList, testSet[docIndex])  # 测试集的词集模型
        if classifyNB(np.array(wordVector), p0V, p1V, pSpam) != testClass[docIndex]:  # 如果分类错误
            errorCount += 1  # 错误计数加1
            print("分类错误的测试集：",testSet[docIndex])
    print('错误率：%.2f%%' % (float(errorCount) / len(testSet) * 100))


if __name__ == '__main__':
    i = 0
    p0V = []
    p1V = []
    pSpam = 0
    while i < 1:
        p0V,p1V,pSpam = spamTest()
        i += 1

    resultTest(p0V,p1V,pSpam)