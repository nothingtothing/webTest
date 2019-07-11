import poplib
import time
import DBaction
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

#六个元素分别存放邮件发件人、收件人、标题、内容文本、是否存在附件(0表示有，2表示无)、附件地址
maillist=['','','','',0,'']

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
#没有这个函数，print出来的会使乱码的头部信息。如'=?gb18030?B?yrXWpL3hufsueGxz?='这种
#通过decode，将其变为中文
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

#解码邮件信息分为两个步骤，第一个是取出头部信息
#首先取头部信息
#主要取出['From','To','Subject']
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
                #value = name + ' < ' + addr + ' > '
                value=name
        maillist[i] = value
        i += 1
        print(header + ':' + value)

#邮件正文部分
#如果存在附件，则可以通过.get_filename()的方式获取文件名称

def get_file(msg):     #取附件
    for part in msg.walk():
        filename=part.get_filename()
        if filename!=None:#如果存在附件
            filename = decode_str(filename)#获取的文件是乱码名称，通过一开始定义的函数解码
            data = part.get_payload(decode = True)#取出文件正文内容
            #定义文件保存路径(附件)
            path=r'G:\Git\Twilight的git\PythonApplication1\PythonApplication1\mailAttachment\%s'%filename
            with open(path, 'wb') as f:
                f.write(data)
            print(filename,'  is downloading...')
            maillist[5] = path

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
            #continue
        email_content_type = ''
        content = ''
        if content_type == 'text/plain':
            email_content_type = 'text'
        elif content_type == 'text/html':
            print('html 格式 跳过')
            continue #不要html格式的邮件
            email_content_type = 'html'
        if charset:
            try:
                content = part.get_payload(decode=True).decode(charset)
            except AttributeError:
                print('type error')
            except LookupError:
                print("unknown encoding: utf-8")
        if email_content_type =='':
            continue
            #如果内容为空，也跳过
        maillist[3] = content
        print(email_content_type + ' -----  ' + content)

#初始化
def EmailInit():
    # 输入邮件地址, 口令和POP3服务器地址:
    email='1678120695@qq.com'
    password='oxlxnspfguthdajc'
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
        msg_content = b'\r\n'.join(lines).decode('utf-8','ignore')
        msg = Parser().parsestr(msg_content)
        #server.dele(index) 删除邮件
        get_header(msg)
        get_file(msg)
        get_content(msg)
        #处理文本格式（删除空格换行等）
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
        maillist[3] = maillist[3].replace('"','“')
        maillist[3] = ''.join(maillist[3].split())
        db.insertEmail(maillist[0],maillist[1],maillist[2],maillist[3],maillist[4])   
    server.quit()

#读取邮件放入数据库
def addNew():
    db = DBaction.DBac()
    db.__init__()
    rows = db.select('Emails')
    num = len(rows)
    while(True):
        # 输入邮件地址, 口令和POP3服务器地址:
        email='1678120695@qq.com'
        password='oxlxnspfguthdajc'
        server=poplib.POP3_SSL('pop.qq.com')
        server.user(email)
        server.pass_(password)
        #登录的过程
        resp, mails, octets = server.list()
        index = len(mails)#邮件的总数
        
        if index > num:
            num = index
            db = DBaction.DBac()
            db.__init__()
            #取邮件
            resp, lines, octets = server.retr(index)
            msg_content = b'\r\n'.join(lines).decode('utf-8','ignore')
            msg = Parser().parsestr(msg_content)
            #server.dele(index) 删除邮件
            get_header(msg)
            get_file(msg)
            get_content(msg)
            #处理文本格式（删除空格换行等）
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
            maillist[3] = maillist[3].replace('"','“')
            maillist[3] = ''.join(maillist[3].split())
            db.insertEmail(maillist[0],maillist[1],maillist[2],maillist[3],maillist[4])
        else:
            server.quit()
            time.sleep(5)
            continue
        server.quit()
        time.sleep(5)

#删除邮件和数据库中信息
def deleteM(i):
    email='1678120695@qq.com'
    password='oxlxnspfguthdajc'
    server=poplib.POP3_SSL('pop.qq.com')
    server.user(email)
    server.pass_(password)
    #登录的过程
    resp, mails, octets = server.list()
    server.dele(i)
    server.quit()

if __name__ == '__main__':
    #EmailInit()
    addNew()
    #deleteM(1)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    #按行存放到数据集中
    # with open('email','w',encoding='utf-8') as file:
     #    for i in range(1,index+1):
      #       with open('mail%s'%i,'r',encoding='utf-8') as f1:
       #          line = f1.read()
        #         file.write(line)
   
        

