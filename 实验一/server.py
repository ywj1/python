import socket
import threading
import json

class Server:
    """
    服务器类
    """
    def __init__(self):
        """
        构造
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__users={}

    def __user_thread(self, user_name):
        """
        用户子线程
        """
        nickname = user_name
        connection = self.__users[user_name]
        print('[Server] 用户', nickname, '加入聊天室')
        self.__broadcast('login',nickname,message='用户 ' + str(nickname) + '加入聊天室')

    def __login_failed(self,user_name,address):
        self.__socket.sendto(json.dumps({
            'type':'login',
            'message': user_name+'用户已注册'
        }).encode(),address)

    def __broadcast(self,type, username, message=''):
        """
        广播
        :param message: 广播内容
        """
        for i in self.__users:
            if i != username:
                self.__socket.sendto(json.dumps({
                    'type': type,
                    'sender_nickname': username,
                    'message': message
                }).encode(),self.__users[i])

    def __secreat(self,type, username, name, message=''):
        '''

        :param type: 格式
        :param username: 发送的人
        :param name: 接受的人
        :param message: 消息
        :return:
        '''
        self.__socket.sendto(json.dumps({
            'type':type,
            'sender_nickname':username,
            'get_nickname':name,
            'message':message
        }).encode(),self.__users[name])

    def start(self):
        """
        启动服务器
        """
        # 绑定端口
        self.__socket.bind(('127.0.0.1', 8888))
        # 启用监听
        print('[Server] 服务器正在运行......')
        # 开始侦听
        while True:
            msg, address = self.__socket.recvfrom(1024)
            print('[Server] 收到一个{}新连接'.format(address))
            # 解析成json数据
            obj = json.loads(msg.decode())
            print(obj)
            # 如果是连接指令，那么则返回一个新的用户编号，接收用户连接
            if obj['type'] == 'login':
                if obj['nickname'] in self.__users:
                    thread = threading.Thread(target=self.__login_failed,args=(obj['nickname'], address))
                    thread.start()
                else:
                    self.__users[obj['nickname']] = address
                    # 开辟一个新的线程
                    thread = threading.Thread(target=self.__user_thread, args=(obj['nickname'], ))
                    thread.start()
            elif obj['type'] == 'broadcast':
                thread = threading.Thread(target=self.__broadcast, args=(obj['type'],obj['user_name'],obj['message'], ))
                thread.start()
            elif obj['type'] == 'secreat':
                self.__secreat(obj['type'],obj['user_name'],obj['to_user'],obj['message'])
            else:
                print('[Server] 无法解析json数据包')

server = Server()
server.start()
