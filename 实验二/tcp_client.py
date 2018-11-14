import socket
import threading
import json
from cmd import Cmd

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

class Client(Cmd):
    '''
    客户端
    '''
    def __init__(self):
        super().__init__()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__username = None

    def __receive_message_thread(self):
        '''
        接受消息线程
        :return:
        '''
        while True:
            buffer = self.__socket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['type'] == 'login':
                print('{}进入游戏房间'.format(obj['send_user']))
            elif obj['type'] == 'yazhu':
                print('[{}]押了{}押了{}{}.'.format(obj['send_user'],obj['kind'],obj['number'],obj['coin']))
            elif obj['type'] == 'first_roll':
                print('新开盘！预叫头彩！')
                print('头彩骰号是{},{}'.format(obj['first_roll'],obj['second_roll']))
            elif obj['type'] == 'Win':
                print('第二次骰子是:{},{}'.format(obj['first_roll'],obj['second_roll']))
                print('恭喜你赢了，返回你{}{}'.format(obj['money'],obj['coin']))
            elif obj['type'] == 'failure':
                print('第二次骰子是:{},{}'.format(obj['first_roll'], obj['second_roll']))
                print('你输了{}'.format(obj['message']))
            else:
                print('没有这个格式')

    def __send_message_thread(self,user_name,type,number,coin):
        '''
        发送线程
        :param type: 押注
        :param number: 数量
        :param coin: 币种
        :return:
        '''
        self.__socket.send(json.dumps({
            'type': 'yazhu',
            'user_name': user_name,
            'kind': type,
            'number': number,
            'coin': coin
        }).encode())


    def start(self):
        self.__socket.connect(('127.0.0.1',8888))
        self.cmdloop()

    def do_login(self,args):
        '''
        登陆
        :param args:
        :return:
        '''
        user_name = args.split(' ')[0]
        self.__socket.send(json.dumps({
            'type': 'login',
            'user_name': user_name
        }).encode())
        self.__username = user_name
        thread = threading.Thread(target=self.__receive_message_thread)
        thread.start()

    def do_ya(self,args):
        '''
        选择押注的方式
        :param args:
        :return:
        '''
        type = args.split(' ')[0]
        number = args.split(' ')[1]
        coin = args.split(' ')[2]
        print('[{}]押{}押了{}{}'.format(self.__username,type,number,coin))
        thread = threading.Thread(target = self.__send_message_thread, args = (self.__username,type,number,coin, ))
        thread.start()

    def do_help(self,arg):
        command = arg.split(' ')[0]
        if command == '':
            print('[Help] login nickname - 登录到聊天室，nickname是你选择的昵称')
            print('[Help] ya type <数量> <coin|silver|gold> - 押注的种类，和押多少钱')
        if command == 'login':
            print('[Help] login nickname - 登录到聊天室，nickname是你选择的昵称')
        if command == 'ya':
            print('[Help] ya type <数量> <coin|silver|gold> - 押注的种类，和押多少钱')
        if command == 'rule':
            print('ya tc <数量> <coin|silver|gold> 押头彩(两数顺序及点数均正确)       一赔三十五\n'
                  'ya dc <数量> <coin|silver|gold> 押大彩(两数点数正确)               一赔十七\n'
                  'ya kp <数量> <coin|silver|gold> 押空盘(两数不同且均为偶数)         一赔五\n'
                  'ya qx <数量> <coin|silver|gold> 押七星(两数之和为七)               一赔五\n'
                  'ya dd <数量> <coin|silver|gold> 押单对(两数均为奇数)               一赔三\n'
                  'ya sx <数量> <coin|silver|gold> 押散星(两数之和为三、五、九、十一)   一赔二\n')

client = Client()
client.start()