#导入模块
import socket
from time import strftime, localtime
from select import select
from json import loads


###建立套接字并设置相关选项
HOST = ''
POST = 9999
ADDR = (HOST, POST)
tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Ipv4,tcp流式
tcpSerSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
#此处为socket设置选项，参数"1",表示将SO_REUSEADDR标记为TRUE，
#操作系统会在服务器socket被关闭或服务器进程终止后
#马上释放该服务器的端口，
#否则操作系统会保留几分钟该端口。
tcpSerSock.bind(ADDR)#绑定ip与端口
tcpSerSock.listen(5)
#允许有多少个未决（等待）的连接在队列中等待，一般设置为5。
tcpSerSock.setblocking(False)
#主要使用的是I/O多路复用而非多线程，所以设置为非阻塞
#否则程序会堵在accept()和recv()等方法这里
inputs = [tcpSerSock]

print('waiting for connnecting...')

while True:
    rlist, wlist, xlist = select(inputs, [], [])
    #通过select进行I/O多路复用，rlist检查可读性
    for s in rlist:
        if s is tcpSerSock:
            tcpCliSock, addr = s.accept()
            print('...connecting from:', addr)
            tcpCliSock.setblocking(False)
            inputs.append(tcpCliSock)
        else:
            data = s.recv(1024)#接收信息，缓冲区为1024字节

            if not data:#用户关闭程序后释放套接字：
                inputs.remove(s)
                s.close()
                continue

            obj = loads(data.decode('utf-8'))
            #loads()将dumps()转成的字符串又重新解析成字典类型。
            
            #Python3以后，socket传递的都是bytes类型的数据，字
            #符串需要先转换一下，string.encode()即可；
            #另一端接收到的bytes数据想转换成字符串，
            #只要bytes.decode()一下就可以。
            #
            time = strftime("%Y-%m-%d %H:%M:%S", localtime())
            data = '{}ONLINE_SPLIT_1.00[{}]{}: {}'.format(len(inputs),time, obj['name'], obj['msg'])
            for sock in inputs:#广播全体：
                if sock is not tcpSerSock:
                    sock.send(data.encode('utf-8'))
