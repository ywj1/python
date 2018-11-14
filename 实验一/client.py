import socket
import threading
import json
from cmd import Cmd

class Client(Cmd):
    '''
    客户端
    '''
    def __init__(self):
        super().__init__()
        self.__socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.__username = None
        self.__aim_address = ('127.0.0.1',8888)

    def __receive_message_thread(self):
        '''
        接受消息线程
        :return:
        '''
        while True:
            buffer = self.__socket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['type'] == 'login':
                print(obj['message'])
            elif obj['type'] == 'broadcast':
                print('['+obj['sender_nickname']+']'+obj['message'])
            elif obj['type'] == 'secreat':
                print('[' + obj['sender_nickname'] + ']' + obj['message'])
            else:
                print('没有这种格式')

    def __broadcast_message_thread(self,type,message):
        '''
        群发发送消息线程
        :param type：群发还是私发
        :param message: 消息
        :return:
        '''
        self.__socket.sendto(json.dumps({
            'type':type,
            'user_name':self.__username,
            'message':message
        }).encode(),self.__aim_address)

    def __secreat_message_thread(self,type,name,message):
        '''
        私发消息
        :param type: 群发还是私发
        :param name: 发送给谁
        :param message: 消息
        :return:
        '''
        self.__socket.sendto(json.dumps({
            'type': type,
            'user_name': self.__username,
            'to_user':name,
            'message': message
        }).encode(), self.__aim_address)


    def start(self):
        """
        启动客户端
        """
        self.cmdloop()

    def do_login(self,args):
        '''
        登陆聊天室
        :param args: 参数
        :return:
        '''
        nickname = args.split(' ')[0]
        self.__socket.sendto(json.dumps({
            'type': 'login',
            'nickname': nickname
        }).encode(),self.__aim_address)
        self.__username = nickname
        thread = threading.Thread(target=self.__receive_message_thread)
        thread.start()

    def do_send_all(self,args):
        '''
        发送消息
        :param args: 参数
        :return:
        '''
        type = args.split(' ')[0]
        message = args.split(' ')[1]
        print('[' + str(self.__username) + ']', message)
        # 开启子线程用于发送数据
        if type == 'broadcast':
            thread = threading.Thread(target=self.__broadcast_message_thread, args=(type,message,))
            thread.start()
        else:
            print('发送格式错误')
    def do_send_secreat(self,args):
        type = args.split(' ')[0]
        name = args.split(' ')[1]
        message = args.split(' ')[2]
        print('[' + str(self.__username) + ']', message)
        if type == 'secreat':
            thread = threading.Thread(target=self.__secreat_message_thread, args=(type,name,message,))
            thread.start()

    def do_help(self,arg):
        """
        帮助
        :param arg: 参数
        """
        command = arg.split(' ')[0]
        if command == '':
            print('[Help] login nickname - 登录到聊天室，nickname是你选择的昵称')
            print('[Help] send message - 发送消息，message是你输入的消息')
            print('[Help] exit -  退出当前用户')
        elif command == 'login':
            print('[Help] login nickname - 登录到聊天室，nickname是你选择的昵称')
        elif command == 'send':
            print('[Help] send message - 发送消息，message是你输入的消息')
        elif command == 'exit':
            print('[Help] exit -  退出当前用户')
        else:
            print('[Help] 没有查询到你想要了解的指令')

client = Client()
client.start()