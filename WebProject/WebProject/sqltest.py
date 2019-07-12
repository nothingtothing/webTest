import poplib
import html
import time
import DBaction
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

email='1678120695@qq.com'
password='veztvpjocggzjbdb2'
password1='veztvpjocggzjbdb'
server='pop.qq.com'

def judgePass(E,P):
    try:
        server = poplib.POP3_SSL('pop.qq.com')
        server.user(E)
        server.pass_(P)
        server.quit()
    except:
        return False
    else:
        return True


