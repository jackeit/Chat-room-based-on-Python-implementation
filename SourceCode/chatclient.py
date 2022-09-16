#导入模块
from tkinter import *
import socket
from tkinter import messagebox
from json import dumps
from threading import Thread
from tkinter.simpledialog import askstring, askinteger, askfloat
class ReceiveThread(Thread):#继承Thread类的类定义
    def __init__(self, tcpCliSock):
        Thread.__init__(self)
        self.daemon = True  # 守护线程
        self.tcpCliSock = tcpCliSock
        
    def run(self):#重写run函数
        while True:
            data = tcpCliSock.recv(1024)#缓冲区为1024字节
            if not data:#退出判定：
                tcpCliSock.close()#关闭连接
                root.destroy()#销毁窗口
            else:#文本框及在线用户表、用户名称更新：
                del online_numbers[0]
                online_numbers.append((data.decode('utf-8').split("ONLINE_SPLIT_1.00")[0]))
                l1.config(text=online_numbers)#人数标签更新
                l2.config(text=NAME[0])#名称标签更新
                Output.insert(END,( data.decode('utf-8').split("ONLINE_SPLIT_1.00")[-1]))
                #文本框更新信息
                

                

def sendMessage():
    # 发送消息：
    #没有输入名称无法发送信息
    if ('unknown' in NAME) or (None in NAME ):
    #dumps函数的用处是将字典(dict)类型的变量转成字符串(str)类型，方便传输
            change_name()
            tcpCliSock.send(dumps({
                'name':'公告',
                'msg':NAME[0]+"正式加入聊天室\n"                  
                
            }).encode('utf-8'))
            #加入后发送信息让服务器广播全体
    else:
          msg = Input.get('1.0', END)
          tcpCliSock.send(dumps({
            'name': NAME[0],
            'msg' : msg
          }).encode('utf-8'))
          Input.delete('1.0', END)#发送完信息后清空输入框
   


def Closing():#退出判定：
    if messagebox.askokcancel("退出", "确定退出吗?"):
        tcpCliSock.send(dumps({
                'name':'公告',
                'msg':NAME[0]+"正式退出聊天室\n"                  
                
            }).encode('utf-8'))
            #退出前发送信息让服务器广播全体
        tcpCliSock.shutdown(socket.SHUT_WR)#关闭套接字


#名称更改：
def change_name():
    if 'unknown' in NAME:
          res = askstring("更改名称", "在发送信息之前,请输入您的新名称")
          if res=="公告":
            messagebox.showinfo(title='无效名称',message='该名称为官方名称，无法被注册，请换另一个名称')
            return
          del NAME[0]
          NAME.append(res)
    else:
          res = askstring("更改名称", "请输入您的新名称")
          if res=="公告":
            messagebox.showinfo(title='无效名称',message='该名称为官方名称，无法被注册，请换另一个名称')
            return
          del NAME[0]
          NAME.append(res)


    
    
    
online_numbers=['1']
###建立套接字并设置相关选项：
HOST = 'localhost'
POST = 9999

ADDR = (HOST, POST)
NAME = ['unknown']

tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Ipv4,tcp流式
tcpCliSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
#此处为socket设置选项，参数"1",表示将SO_REUSEADDR标记为TRUE，
#操作系统会在服务器socket被关闭或服务器进程终止后
#马上释放该服务器的端口，
#否则操作系统会保留几分钟该端口。
tcpCliSock.connect(ADDR)#绑定ip与端口

###主窗口设置：
root = Tk()
s_width= root.winfo_screenwidth()
s_height = root.winfo_screenheight()
root.geometry('+{}+{}'.format((s_width-450)//2, (s_height-350)//2))
root.title('Python聊天群 ')

###文本窗口和输入窗口：
frameT = Frame(root, width=460, height=320)
frameB = Frame(root, width=460, height=80)
frameT.pack(expand='yes', fill='both')
frameB.pack(expand='yes', fill='both')
Input = Text(frameB, height=6)
Output = Text(frameT)
Input.pack(expand='yes', fill='both')
Output.pack(expand='yes', fill='both')

Output.bind('<KeyPress>', lambda e: 'break')
#文本框不可更改

scrollbar = Scrollbar(frameT, command=Output.yview, orient=VERTICAL) 
Output.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side='right', fill='y')
#信息滑动条

#在线人数展示：
Label(frameT, text='在线人数：').pack(side=LEFT,padx=25)
l1 = Label(frameT, text='加载中')
l1.pack(side=LEFT)

#####用户名称显示：
Label(frameT, text='名称：').pack(side=LEFT,padx=25)
l2 = Label(frameT, text='加载中')
l2.pack(side=LEFT)

###功能按键设置：
Button(frameT,text="改名称",width=8, bg='DodgerBlue', fg='White', command=change_name).pack(side=LEFT,padx=40)
btnFrame = Frame(frameB, height=24, background='White')
btnFrame.pack(expand='yes', fill='both')
Button(btnFrame, text='发送', width=8, bg='DodgerBlue', fg='White', command=sendMessage).pack(side=RIGHT)

ReceiveThread(tcpCliSock).start()  # 启动消息接收线程
root.protocol("WM_DELETE_WINDOW", Closing)  # 退出时处理
root.mainloop()#主窗口循环