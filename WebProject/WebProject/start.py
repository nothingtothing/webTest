#created by 衣春腾，李星星
from flask import Flask,render_template
from flask import request
from test import joint,getFocusname
from flask_script import Manager, Shell
from flask_mail import Mail, Message
from threading import Thread
from sqltest import judgePass
import os
import pandas as pd
import json
import DBaction
import poplib
import html
import time
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

#六个元素分别存放邮件发件人、收件人、标题、内容纯文本、是否存在附件(0表示有，2表示无)、是否被屏蔽(Block)，html文本，附件位置
maillist=['F','T','TI','',0,'','','']

#获取邮件的字符编码，首先在message中寻找编码，如果没有，就在header的Content-Type中寻找
def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos+8:].strip()
    return charset

#解析消息头中的字符串
#通过decode，将其变为中文
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

#主要取出头部信息['From','To','Subject']
def get_header(msg):
    i = 0
    for header in ['From', 'To', 'Subject']:
        value = msg.get(header, '')
        if value:
            #文章的标题有专门的处理方法
            if header == 'Subject':
                value = decode_str(value)
            else:
                hdr, addr = parseaddr(value)
                name = decode_str(addr)
                value=name
        maillist[i] = value
        i += 1

#获得附件储存到本地（如果有）
def get_file(msg):     #取附件
    for part in msg.walk():
        filename=part.get_filename()
        if filename!=None:#如果存在附件
            filename = decode_str(filename)
            data = part.get_payload(decode = True)#取出文件正文内容
            #定义文件保存路径(附件)
            with open(path, 'wb') as f:
                f.write(data)
            print(filename,'  is downloading...')
            maillist[7] = path

#解析获得纯文本
def get_content(msg):
    for part in msg.walk():
        content_type = part.get_content_type()
        charset = guess_charset(part)
        #如果有附件，则直接跳过，并标记为0，反之为2
        if part.get_filename()!=None:
            maillist[4] = 0
            continue
        else:
            maillist[4] = 2 
        email_content_type = ''
        content = ''
        if content_type == 'text/plain':
            email_content_type = 'text'
        elif content_type == 'text/html':
            continue
            email_content_type = 'html'
        if charset:
            try:
                content = part.get_payload(decode=True)
                content= content.decode(charset)
            except AttributeError:
                print('type error')
            except LookupError:
                print("unknown encoding: utf-8")
        if email_content_type =='':
            continue
            #如果内容为空，也跳过
        maillist[3] = content

#解析获得html

def get_html(msg, indent=0):
    if (msg.is_multipart()):
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            get_html(part, indent + 1)
    else:
        content_type = msg.get_content_type()
        if content_type=='text/plain' or content_type=='text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)    
            maillist[6] = content

#将文本处理成能存放到数据库的形式
def text_processing():
    try:#处理文本格式（删除空格换行等）
        maillist[2] = maillist[2].replace(',',' ')
        maillist[3] = maillist[3].replace('\n','')
        maillist[3] = maillist[3].replace(',','，')
        #""替换为“”
        num2 = 1
        for i in range(0,len(maillist[3])):
            if maillist[3][i] == '"':
                if num2 % 2 == 1:
                    maillist[3] = maillist[3].replace('"','“',1)
                elif num2 % 2 == 0:
                    maillist[3] = maillist[3].replace('"','”',1)
            num2 += 1
        maillist[3] = maillist[3].replace('\'','‘')
        maillist[3] = ''.join(maillist[3].split())
        maillist[6] = maillist[6].replace('\'','#')
    except Exception as e:
        print('请检查文本格式是否为utf-8',e)


def list_clear():
    #清空maillist内容
    maillist=['','','','',0,'','','']

#把html文本存放到本地文件
def html_download():
    db = DBaction.DBac()
    db.__init__()
    id = db.selectID()
    try:
        with open('html%d.html'%id,'w',encoding='utf-8') as f:
            f.write(maillist[6])
    except Exception as e:
        print('打开文件失败',e)
#初始化
def EmailInit():
    # 输入邮件地址, 口令和POP3服务器地址:
    email='1678120695@qq.com'
    password='veztvpjocggzjbdb'
    server=poplib.POP3_SSL('pop.qq.com')
    server.user(email)
    server.pass_(password)
    #登录的过程
    resp, mails, octets = server.list()
    index = len(mails)#邮件的总数
        
    #循环取所有邮件
    db = DBaction.DBac()
    db.__init__()
    for i in range(1,index+1):
        #取邮件
        resp, lines, octets = server.retr(i)
        msg_content = b'\r\n'.join(lines).decode('utf-8')
        msg = Parser().parsestr(msg_content)
        get_header(msg)
        if i == 1:
            print(maillist[1])
            db1 = DBaction.DBac()
            db1.insertUser(maillist[1],email,password)
        get_file(msg)
        get_content(msg)
        get_html(msg)
        text_processing()
        html_download()
        list_clear()
        db.insertEmailTest(i,maillist[0],maillist[1],maillist[2],maillist[3],maillist[4],maillist[5],maillist[6],maillist[7])      
    server.quit()


#读取邮件放入数据库
def addNew():
    db = DBaction.DBac()
    db.__init__()
    rows = db.select('emailTest')
    num = len(rows)
    
        # 输入邮件地址, 口令和POP3服务器地址:
    email='1678120695@qq.com'
    password='veztvpjocggzjbdb'
    server=poplib.POP3_SSL('pop.qq.com')
    server.user(email)
    server.pass_(password)
        #登录的过程
    resp, mails, octets = server.list()
    index = len(mails)#邮件的总数

    if index > num:
        count = index - num
        print(count)
        num = index
        for i in range(1,count+1):
            resp, lines, octets = server.retr(index-count + i)  #取邮件
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            msg = Parser().parsestr(msg_content)
            get_header(msg)
                #get_file(msg)
            get_content(msg)
            get_html(msg)
            text_processing()
                #html_download()
            list_clear()
            db.insertEmailTest(index-count + i,maillist[0],maillist[1],maillist[2],maillist[3],maillist[4],maillist[5],maillist[6],maillist[7])   
            print('您有新的邮件！')        
    #else:      
    server.quit()

#删除邮件和数据库中信息
def deleteM(i):
    email='1678120695@qq.com'
    password='veztvpjocggzjbdb'
    server=poplib.POP3_SSL('pop.qq.com')
    server.user(email)
    server.pass_(password)
    #登录的过程
    resp, mails, octets = server.list()
    server.dele(i)
    server.quit()

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = '1678120695@qq.com'
app.config['MAIL_PASSWORD'] = 'veztvpjocggzjbdb'

mail = Mail(app)


ham,spam=joint()
focusname=getFocusname()


db = DBaction.DBac()
db.__init__()

#判断是否有特别关注来信
def judgeFocusname():
    a = 'b'
    for eachHam in ham: 
        if(eachHam['from'] in focusname):
            a="a"
    return a
#登录页
@app.route("/")
def login():
    return render_template("login.html")

#特别提醒
@app.route("/showfocus")
def showfocus():
    b = judgeFocusname()
    print(b)
    return b

#邮箱主页
@app.route("/showmain",methods=["POST"])
def start():
    username = request.form.get('username')
    password = request.form.get('password')
    a = judgePass(username,password)
    if (a):
            nums = db.select("emailTest")
            num = len(ham)
            blackwords = db.select("BadWords")
            focusnames = db.select("Focusnames")
            blacknames = db.select("BadNames")
            whitelist = db.select("Whitelist")
            return render_template("index.html",amount=num,words=blackwords,emailuser=username,
                                   blockedfroms=blacknames,whitelists=whitelist,focusedpeople=focusnames,emails=ham)
    else:
       return render_template("login.html")

#帮助界面
@app.route("/docs")
def showhelp():
    return render_template("docs.html")
#删除邮件
def delHamItem(id):
    i=-1
    for eachHam in ham:
        i=i+1
        if(eachHam['id']==id):
            del ham[i]
            for eachHam in ham:
                if(eachHam['id']>id):
                    eachHam['id']=eachHam['id']-1
            for eachSpam in spam:
                if(eachSpam['id']>id):
                    eachSpam['id']=eachSpam['id']-1
          
def delSpamItem(id):
    i=-1
    for eachSpam in spam:
        i=i+1
        if(eachSpam['id']==id):
            del spam[i]
            for eachHam in ham:
                if(eachHam['id']>id):
                    eachHam['id']=eachHam['id']-1
            for eachSpam in spam:
                if(eachSpam['id']>id):
                    eachSpam['id']=eachSpam['id']-1
#发送邮件
@app.route("/sendmessage")
def sendmessage():
    title = request.args['subject']
    geter = request.args['receiver']
    content = request.args['message']
    print(title)
    print(geter)
    msg = Message(title, sender='1678120695@qq.com', recipients=[geter])
    msg.body = content
    with app.app_context():
        mail.send(msg)
    print(title)
    print(geter)
    return 'success'

#垃圾邮件切换
@app.route("/showspams")
def showspams():
    spams = json.dumps(spam)
    return spams
#非垃圾邮件切换
@app.route("/showhams")
def showhams():
    hams = json.dumps(ham)
    return hams
#删除邮件
@app.route("/deletemail")
def deletemail():
    delID=request.args['Id']
    db.deleteMail(int(delID))
    deleteM(int(delID))
    delHamItem(int(delID))
    hams = json.dumps(ham)
    return hams

@app.route("/deletespam")
def deletespam():
    delID=request.args['Id']
    db.deleteMail(int(delID))
    deleteM(int(delID))
    delSpamItem(int(delID))
    spams = json.dumps(spam)
    return spams

#更新过滤词
@app.route("/blackwords")
def updatewords():
    keyword = request.args['keyword']
    db.delete("BadWords","ID",keyword)
    blackwords = db.select("BadWords")
    BlackWords = []
    for word in blackwords:
        dict = {}
        dict['id'] = word[1]
        dict['key'] = word[0]
        BlackWords.append(dict)
    BlackWord = json.dumps(BlackWords)
    return BlackWord

#更新黑名单
@app.route("/blockedfrom")
def updatefroms():
    keyword1 = request.args['keyword1']
    db.delete("BadNames","ID",keyword1)
    blockedfroms = db.select("BadNames")
    BlockedFroms = []
    for eachfrom in blockedfroms:
        dict = {}
        dict['id'] = eachfrom[1]
        dict['key'] = eachfrom[0]
        BlockedFroms.append(dict)
    BlockedFrom = json.dumps(BlockedFroms)
    return BlockedFrom

#更新白名单
@app.route("/whitelist")
def updatewhitelists():
    keyword2 = request.args['keyword2']
    db.delete("Whitelist","ID",keyword2)
    whitelists = db.select("Whitelist")
    Whitelists = []
    for eachlist in whitelists:
        dict = {}
        dict['id'] = eachlist[1]
        dict['key'] = eachlist[0]
        Whitelists.append(dict)
    Whitelist = json.dumps(Whitelists)
    print(Whitelist)
    return Whitelist
#更新特别关注名单
@app.route("/focuslist")
def updatefocuslists():
    keyword3 = request.args['keyword3']
    db.delete("Focusnames","ID",keyword3)
    focuslists = db.select("Focusnames")
    Focuslists = []
    for eachlist in focuslists:
        dict = {}
        dict['id'] = eachlist[1]
        dict['key'] = eachlist[0]
        Focuslists.append(dict)
    Focuslist = json.dumps(Focuslists)
    return Focuslist
#添加黑白名单，过滤词，特别关注
@app.route("/addnewword")
def addnewword():
    newword = request.args['Newword']
    db.insert("BadWords","words",newword)
    blackwords = db.select("BadWords")
    BlackWordss = []
    for word in blackwords:
        dict = {}
        dict['id'] = word[1]
        dict['key'] = word[0]
        BlackWordss.append(dict)
    BlackWord1 = json.dumps(BlackWordss)
    print(BlackWord1)
    return BlackWord1

@app.route("/addblacknames")
def addblackname():
    newword = request.args['Newword1']
    db.insert("BadNames","blackMail",newword)
    blacknames = db.select("BadNames")
    BlackNames = []
    for word in blacknames:
        dict = {}
        dict['id'] = word[1]
        dict['key'] = word[0]
        BlackNames.append(dict)
    BlackName = json.dumps(BlackNames)
    return BlackName

@app.route("/addwhitenames")
def addwhitename():
    newword = request.args['Newword2']
    db.insert("Whitelist","name",newword)
    whitenames = db.select("Whitelist")
    WhiteNames = []
    for word in whitenames:
        dict = {}
        dict['id'] = word[1]
        dict['key'] = word[0]
        WhiteNames.append(dict)
    WhiteName = json.dumps(WhiteNames)
    return WhiteName

@app.route("/addfocusnames")
def addfocusname():
    newword = request.args['Newword3']
    db.insert("Focusnames","focusname",newword)
    focusnames = db.select("Focusnames")
    FocusNames = []
    for word in focusnames:
        dict = {}
        dict['id'] = word[1]
        dict['key'] = word[0]
        FocusNames.append(dict)
    FocusName = json.dumps(FocusNames)
    return FocusName

if __name__ == '__main__':
    addNew()
    app.run(host = '0.0.0.0', port = 8000)

