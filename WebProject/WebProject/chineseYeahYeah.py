import jieba
'''
text_path = "init.txt"
isCN = 1
text = open( text_path, encoding='utf-8').read()      #打开文本，获取内容
'''

stopwords_path = "stopwords_cn.txt"

def jiebaclearText(text): 
    mywordlist = []                                #存放最终分词结果
    seg_list = jieba.cut(text, cut_all=False)
    #print(seg_list)
    liststr="/ ".join(seg_list)                      #未经处理的文本分词结果列表
    #print(liststr)
    f_stop = open(stopwords_path, encoding='utf-8')     #打开停用词词表
    try:
        f_stop_text = f_stop.read( )                      #获取停用词词表中的内容
    finally:
        f_stop.close( )
    f_stop_seg_list = f_stop_text.split('\n')
    for myword in liststr.split('/'):      #获取初次分词结果中的每一个词
        if not(myword.strip() in f_stop_seg_list) and len(myword.strip())>1:
            mywordlist.append(myword)
    #print(mywordlist)
    return ''.join(mywordlist)

'''
if isCN:   #开启中文分词
    text = jiebaclearText(text)         #获得中文分词结果  
'''

def clearText(stopwordsPath,textPath):
    text_path = textPath
    text = open( text_path, encoding='utf-8').read()
    stopwords_path = stopwordsPath
    text = jiebaclearText(text)
    print(text)

