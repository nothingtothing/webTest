from flask import Flask,render_template
from flask import request
from test import joint,getFocusname
from flask_script import Manager, Shell
from flask_mail import Mail, Message
from threading import Thread
from papapa import guess_charset, addNew,decode_str,get_header,EmailInit
from sqltest import judgePass
import os
import pandas as pd
import json
import DBaction

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
    a = 0
    for eachHam in ham: 
        if(eachHam['from'] in focusname):
            a=1
    return a
#登录页
@app.route("/")
def login():
    return render_template("login.html")


@app.route("/shoufocus")
def shoefocus():
    b = judgeFocusname()
    return b;

#邮箱主页
@app.route("/showmain",methods=["POST"])
def start():
    username = request.form.get('username')
    password = request.form.get('password')
    a = judgePass(username,password)
    if (a):
            
            print(app.config['MAIL_USERNAME'])
            print(app.config['MAIL_USERNAME'])
            nums = db.select("emailTest")
            num = len(ham)
            blackwords = db.select("BadWords")
            focusnames = db.select("Focusnames")
            blacknames = db.select("BadNames")
            whitelist = db.select("Whitelist")
            return render_template("index.html",amount=num,words=blackwords,blockedfroms=blacknames,whitelists=whitelist,focusedpeople=focusnames,emails=ham)
    else:
       return render_template("login.html")


@app.route("/docs")
def showhelp():
    return render_template("docs.html")

def delHamItem(id):
    i=-1
    for eachHam in ham:
        i=i+1
        if(eachHam['id']==id):
            del ham[i]

def delSpamItem(id):
    i=-1
    for eachSpam in spam:
        i=i+1
        if(eachSpam['id']==id):
            del spam[i]


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

@app.route("/showspams")
def showspams():
    spams = json.dumps(spam)
    return spams

@app.route("/showhams")
def showhams():
    hams = json.dumps(ham)
    return hams

@app.route("/deletemail")
def deletemail():
    delID=request.args['Id']
    db.delete("emailTest","ID",delID)
    delHamItem(int(delID))
    hams = json.dumps(ham)
    return hams

@app.route("/deletespam")
def deletespam():
    delID=request.args['Id']
    db.delete("emailTest","ID",delID)
    ham,spam=joint()
    spams = json.dumps(spam)
    return spams


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
    app.run(host = '0.0.0.0', port = 80)

