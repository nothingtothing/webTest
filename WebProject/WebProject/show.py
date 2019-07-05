from flask import Flask,render_template
from flask import request
from realTest import testModelBySame
import pandas as pd
import  json

app = Flask(__name__)

path = "../data/email"
df = testModelBySame(path)
#print(df)

all = []
for index, row in df.iterrows():
    dict ={}
    dict['frome']=row['frome'] 
    dict['to']=row['to']
    dict['title']=row['title']
    dict['content']=row['content']
    dict['classes']=(int)(row['classes'])
    all.append(dict)


ham = []
spam = []
dfHam = df[df['classes'] == 1]
dfSpam = df[df['classes'] == 0]

for index, row in dfHam.iterrows():
    dict ={}
    dict['frome']=row['frome'] 
    dict['to']=row['to']
    dict['title']=row['title']
    dict['content']=row['content']
    dict['classes']=(int)(row['classes'])
    ham.append(dict)

for  index, row in dfSpam.iterrows():
    dict ={}
    dict['frome']=row['frome'] 
    dict['to']=row['to']
    dict['title']=row['title']
    dict['content']=row['content']
    dict['classes']=(int)(row['classes'])
    spam.append(dict)



@app.route("/")
def show():
    return render_template("2.html",hams=ham,spams=spam)

if __name__ == '__main__':

    app.run(debug=True)
