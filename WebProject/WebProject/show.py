from flask import Flask,render_template
from flask import request
from test import joint
from flask_script import Manager, Shell
from flask_mail import Mail, Message
from threading import Thread
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

db = DBaction.DBac()
db.__init__()



ham,spam=joint()

@app.route("/")
def show():
    rows = db.select("BadWords")
    users = db.select("BadNames")
    return render_template("2.html",hams=ham,spams=spam,keywords=rows,names=users)

@app.route("/wordaction",methods = ["GET","POST"])
def addword():
    word = request.form.get("uname")
    db.insert("BadWords",word)
    rows = db.select("BadWords")
    users = db.select("BadNames")
    return render_template("addkey.html",hams=ham,spams=spam,keywords=rows,names=users)

@app.route("/worddelaction",methods=["GET","POST"])
def delkey():
    word = request.form.get("delword")
    db.delete("BadWords","words",word)

    rows = db.select("BadWords")
    users = db.select("BadNames")
    return render_template("addkey.html",hams=ham,spams=spam,keywords=rows,names=users)


@app.route("/useraction",methods=["GET","POST"])
def adduser():
    user = request.form.get("username")
    db.insert("BadNames",user)
    rows = db.select("BadWords")
    users = db.select("BadNames")
    return render_template("addkey.html",hams=ham,spams=spam,keywords=rows,names=users)

@app.route("/userdelaction",methods=["GET","POST"])
def deluser():
    user = request.form.get("deluser")
    db.delete("BadNames","blackMail",user)
    rows = db.select("BadWords")
    users = db.select("BadNames")
    return render_template("addkey.html",hams=ham,spams=spam,keywords=rows,names=users)


@app.route("/blackinfo",methods=["GET","POST"])
def addkey():
    users = db.select("BadNames")
    rows = db.select("BadWords")
    return render_template("addkey.html",hams=ham,spams=spam,keywords=rows,names=users)


@app.route("/send",methods=["GET","POST"])
def sendmail():
    title = request.form.get("Topic")
    geter = request.form.get("geter")
    content = request.form.get("content")
    msg = Message(title, sender='1078176775@qq.com', recipients=[geter])
    msg.body = content
    with app.app_context():
        mail.send(msg)
    rows = db.select("BadWords")
    users = db.select("BadNames")
    return render_template("2.html",hams=ham,spams=spam,keywords=rows,names=users)

       


if __name__ == '__main__':

    app.run(debug=True)
    conn.close()