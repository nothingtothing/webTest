#by 李星星

import poplib
import html
import time
import DBaction
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
        db.insertEmailTest(maillist[0],maillist[1],maillist[2],maillist[3],maillist[4],maillist[6],maillist[7])   
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
            db.insertEmailTest(maillist[0],maillist[1],maillist[2],maillist[3],maillist[4],maillist[6],maillist[7])
            print('您有新的邮件！')        
    else:
        server.quit()
        time.sleep(5)
        
    server.quit()
    time.sleep(3)

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

if __name__ == '__main__':
    #初始化（爬取邮箱所有邮件并存放到数据库）
    #EmailInit()
    #判断是否有新的邮件，有就加入数据库
    addNew()
    #按索引序号删除，1表示最新邮件，以此类推index为最后一封邮件
    #deleteM(1)