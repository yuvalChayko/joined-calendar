# ClientComm - responsible for communication with the server

import socket
import threading
import sys
import random
from encryption import Encryption
import queue


class ClientComm:
    def __init__(self, server_ip, port, recv_q):
        self.server_ip = server_ip
        self.port = port
        self.recv_q = recv_q
        self.socket = socket.socket()
        self.key = None
        self.g = 6269
        self.p = 1433
        self.encryption = None
        threading.Thread(target=self._main_loop, ).start()


    def _main_loop(self):
        """
        connect to server and then get msgs from him
        :return:
        """
        try:
            self.socket.connect((self.server_ip, self.port))
        except Exception as e:
            sys.exit("server is down, try again later")
        self._set_key()
        while not self.encryption:
            pass

        while True:
            try:
                data_len = int(self.socket.recv(3).decode())
                data = self.socket.recv(data_len)
            except Exception as e:
                sys.exit("server is down, try again later")

            self.recv_q.put(self.encryption.decrypt(data)) # decrypted data


    def send(self, msg):
        '''
        send msg to server
        :param msg: str
        :return:
        '''
        while not self.encryption:
            pass
        msg = self.encryption.encrypt(msg)
        try:
            self.socket.send(str(len(msg)).zfill(3).encode())
            self.socket.send(msg)
        except Exception as e:
            print('client comm - send', str(e))
            sys.exit("server is down, try again later")

    def _set_key(self):
        """
        set key
        :return:
        """
        try:
            data_len = int(self.socket.recv(3).decode())
            data = self.socket.recv(data_len).decode()
        except Exception as e:
            sys.exit("server is down, try again later")

        random_num = random.randint(0, self.p-3)+1
        personal_key = "50" + str(self.g ** random_num % self.p)
        try:
            self.socket.send(str(len(personal_key)).zfill(3).encode())
            self.socket.send(personal_key.encode())
        except Exception as e:
            print("client comm - set key ", str(e))

        key = str(int(data[2:]) ** random_num % self.p)
        self.encryption = Encryption(key)


if __name__ == '__main__':
    msg_q = queue.Queue()
    comm = ClientComm('127.0.0.1', 4500, msg_q)
    comm.send("hello")
    print(msg_q.get())
