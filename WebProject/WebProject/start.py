from flask import Flask,render_template
from flask import request
from test import joint
from flask_script import Manager, Shell
from flask_mail import Mail, Message
from threading import Thread
from papapa import guess_charset, addNew,decode_str,get_header,EmailInit
import os
import pandas as pd
import json
import DBaction

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '1078176775@qq.com'
app.config['MAIL_PASSWORD'] = 'fhfktworiggwhheh'
mail = Mail(app)


ham,spam=joint()

db = DBaction.DBac()
db.__init__()

@app.route("/")
def start():
    nums = db.select("emailTest")
    num = len(nums)
    blackwords = db.select("BadWords")
    blacknames = db.select("BadNames")
    whitelist = db.select("Whitelist")
    return render_template("index.html",amount=num,words=blackwords,blockedfroms=blacknames,whitelists=whitelist,emails=ham)

@app.route("/sendmessage",methods=["POST","GET"])
def sendmessage():
    nums = db.select("Emails")
    num = len(nums)
    blackwords = db.select("BadWords")
    blacknames = db.select("BadNames")
    whitelist = db.select("Whitelist")
    title = request.form.get("subject")
    geter = request.form.get("email")
    content = request.form.get("message")
    msg = Message(title, sender='1078176775@qq.com', recipients=[geter])
    msg.body = content
    with app.app_context():
        mail.send(msg)
    return render_template("index.html",amount=num,words=blackwords,blockedfroms=blacknames,whitelists=whitelist,emails=ham)


@app.route("/showspams")
def showspams():
    ham,Spam=joint()
    spams = json.dumps(Spam)
    return spams

@app.route("/showhams")
def showhams():
    Ham,Spam=joint()
    hams = json.dumps(Ham)
    return hams

@app.route("/deletemail")
def deletemail():
    delID=request.args['Id']
    db.delete("Emails","ID",delID)
    ham,spam=joint()
    hams = json.dumps(ham)
    return hams



@app.route("/blackwords")
def updatewords():
    keyword = request.args['keyword']
    db.delete("BadWords","words",keyword)
    blackwords = db.select("BadWords")
    BlackWords = []
    for word in blackwords:
        dict = {}
        dict['key'] = word[0]
        BlackWords.append(dict)
    BlackWord = json.dumps(BlackWords)
    return BlackWord


@app.route("/blockedfrom")
def updatefroms():
    keyword1 = request.args['keyword1']
    db.delete("BadNames","blackMail",keyword1)
    blockedfroms = db.select("BadNames")
    BlockedFroms = []
    for eachfrom in blockedfroms:
        dict = {}
        dict['key'] = eachfrom[0]
        BlockedFroms.append(dict)
    BlockedFrom = json.dumps(BlockedFroms)
    return BlockedFrom

@app.route("/whitelist")
def updatewhitelists():
    keyword2 = request.args['keyword2']
    db.delete("Whitelist","name",keyword2)
    whitelists = db.select("Whitelist")
    Whitelists = []
    for eachlist in whitelists:
        dict = {}
        dict['key'] = eachlist[0]
        Whitelist.append(dict)
    Whitelist = json.dumps(Whitelists)
    return Whitelist


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8000)

