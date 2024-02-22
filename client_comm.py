import socket
import threading
import sys
import random
from encryption import Encryption


class ClientComm:
    def __init__(self, server_ip, port, recv_q):
        self.server_ip = server_ip
        self.port = port
        self.recv_q = recv_q
        self.socket = socket.socket()
        # self.key = None
        # self.g = 6269
        # self.p = 1433
        # self.personal_key = random.randint(self.p-3)+1
        # self.encryption = None
        threading.Thread(target=self._main_loop, ).start()

    def _main_loop(self):
        try:
            self.socket.connect((self.server_ip, self.port))
        except Exception as e:
            sys.exit("server is down, try again later")
        # try:
        #     self.socket.send(f"07{self.g ** self.personal_key % self.p}".encode())
        # except Exception as e:
        #     sys.exit()

        while True:
            try:
                data_len = int(self.socket.recv(3).decode())
                data = self.socket.recv(data_len).decode()
            except Exception as e:
                sys.exit("server is down, try again later")
            # if self.encryption == None:
            #     self.recv_q.put(data)
            # else:
            #     self.recv_q.put(self.decryption(data)) # decrypted data
            self.recv_q.put(data)


    def send(self, msg):
        '''
        send msg to server
        :param msg: str
        :return:
        '''

        try:
            self.socket.send(str(len(msg)).zfill(3).encode())
            self.socket.send(msg.encode())
        except Exception as e:
            print('client comm - send', str(e))
            sys.exit("server is down, try again later")

    def _set_key(self):
        pass
