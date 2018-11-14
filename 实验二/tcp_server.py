import socket
import threading
import json
from random import randint

#  我真诚地保证：
#  我自己独立地完成了整个程序从分析、设计到编码的所有工作。
#  如果在上述过程中，我遇到了什么困难而求教于人，那么，我将在程序实习报告中
#  详细地列举我所遇到的问题，以及别人给我的提示。
#  在此，我感谢 github对我的启发和帮助。下面的报告中，我还会具体地提到
#  他们在各个方法对我的帮助。
#  我的程序里中凡是引用到其他程序或文档之处，
#  例如教材、课堂笔记、网上的源代码以及其他参考书上的代码段,
#  我都已经在程序的注释里很清楚地注明了引用的出处。

#  我从未没抄袭过别人的程序，也没有盗用别人的程序，
#  不管是修改式的抄袭还是原封不动的抄袭。
#  我编写这个程序，从来没有想过要去破坏或妨碍其他计算机系统的正常运转。
#  陈奔 改成自己的名字
class Server:
    """
    服务器类
    """
    def __init__(self):
        """
        构造
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__users = {}
        self.__F_first_roll = None
        self.__F_second_roll = None
        self.__S_first_roll = None
        self.__S_second_roll = None
        self.__yazhu = {}

    def __roll(self):
        return randint(1, 6)


    def __broadcast_login(self,user_name):
        '''
        发送登陆消息
        :param user_name: 登陆的人
        :return:
        '''
        for i in self.__users:
            if i != user_name:
                self.__users[i].send(json.dumps({
                    'type': 'login',
                    'send_user': user_name
                }).encode())

    def __broadcast_yazhu(self,user_name,kind,number,coin):
        '''
        发送押注消息
        :param user_name: 谁押注
        :param kind: 类型
        :param number: 数量
        :param coin: coin
        :return:
        '''
        for i in self.__users:
            if i != user_name:
                self.__users[i].send(json.dumps({
                    'type': 'yazhu',
                    'send_user': user_name,
                    'kind': kind,
                    'number': number,
                    'coin': coin
                }).encode())

    def __broadcast(self):
        '''
        发送第一个骰子信息
        :return:
        '''
        first_roll = self.__roll()
        self.__F_first_roll = first_roll
        second_roll = self.__roll()
        self.__F_second_roll = second_roll
        for i in self.__users:
            self.__users[i].send(json.dumps({
                'type': 'first_roll',
                'first_roll': first_roll,
                'second_roll': second_roll
            }).encode())

    def __send_touzi(self):
        '''
        第二次投骰子
        :return:
        '''
        peilv = None
        type = None
        first_roll = self.__roll()
        self.__S_first_roll = first_roll
        second_roll = self.__roll()
        self.__S_second_roll = second_roll
        if first_roll == self.__F_first_roll and second_roll == self.__F_second_roll:
            peilv = 36
            type = 'tc'
        elif first_roll == self.__F_second_roll and second_roll == self.__F_first_roll:
            peilv = 17
            type = 'dc'
        elif (first_roll != second_roll) and first_roll%2 == 0 and second_roll%2 == 0:
            peilv = 5
            type = 'kp'
        elif first_roll+second_roll == 7:
            peilv = 5
            type = 'qx'
        elif first_roll%2 == 1 and second_roll%2 == 1:
            peilv = 3
            type = 'dd'
        elif (first_roll+second_roll) in [2, 3, 5, 9, 11]:
            peilv = 2
            type = 'sx'
        else:
            perlv = 0
            type = 'gg'

        return type, peilv

    def __send_money(self,user_name,money,coin):
        '''
        发钱
        :return:
        '''
        self.__users[user_name].send(json.dumps({
            'type': 'Win',
            'money': money,
            'coin': coin,
            'first_roll': self.__S_first_roll,
            'second_roll': self.__S_second_roll
        }).encode())

    def __send_failure(self,user_name):
        '''
        发送gg
        :return:
        '''
        self.__users[user_name].send(json.dumps({
            'type': 'failure',
            'message': 'GG',
            'first_roll': self.__S_first_roll,
            'second_roll': self.__S_second_roll
        }).encode())

    def start(self):
        """
        启动服务器
        :return:
        """
        Num_user = 2
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(('127.0.0.1',8888))
        # 启用监听
        self.__socket.listen(Num_user)
        print('[Server] 服务器正在运行......')
        ready = 0
        start = 0
        while True:
            connection, address = self.__socket.accept()
            if connection not in self.__users.values():
                while True:
                    print('[Server] 收到一个新连接')
                    buffer = connection.recv(1024).decode()
                    # 解析成json数据
                    obj = json.loads(buffer)
                    #登陆
                    if obj['type'] == 'login':
                        self.__users[obj['user_name']] = connection
                        thread = threading.Thread(target = self.__broadcast_login, args = (obj['user_name'], ))
                        thread.setDaemon(1)
                        thread.start()
                        ready += 1
                    #开始游戏
                    if ready == Num_user:
                        thread = threading.Thread(target = self.__broadcast)
                        thread.setDaemon(1)
                        thread.start()
                        ready = 0
                    break

            if connection in self.__users.values():
                while True:
                    if ready != 0 and ready != Num_user:
                        break
                    for i in self.__users:
                        sock = self.__users[i]
                        buffer = sock.recv(1024).decode()
                        # 解析成json数据
                        obj = json.loads(buffer)
                        #押注
                        if obj['type'] == 'yazhu':
                            start += 1
                            self.__yazhu[obj['user_name']] = [obj['kind'],obj['number'],obj['coin']]
                            thread = threading.Thread(target = self.__broadcast_yazhu, args = (obj['user_name'],obj['kind'],obj['number'],obj['coin'],))
                            thread.start()

                        if start == Num_user:
                            type, peilv = self.__send_touzi()
                            for i in self.__yazhu:
                                if self.__yazhu[i][0] == type:
                                    money = (peilv+1) * int(self.__yazhu[i][1])
                                    self.__send_money(i,money,self.__yazhu[i][2])
                                else:
                                    self.__send_failure(i)
                            start = 1



server = Server()
server.start()