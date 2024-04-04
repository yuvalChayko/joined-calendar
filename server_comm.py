import select
import socket
import threading
import queue
import random
from encryption import Encryption


class ServerComm:

    def __init__(self, port, rcv_q):
        self.port = port
        self.rcv_q = rcv_q
        self.socket = socket.socket()
        # socket: [ip, encryption]
        self.open_clients = {}
        self.is_running = False
        self.count = 1
        self.g = 6269
        self.p = 1433
        threading.Thread(target=self._main_loop).start()

    def _main_loop(self):
        self.socket.bind(("0.0.0.0", self.port))
        self.socket.listen(3)
        self.is_running = True
        while self.is_running:
            rlist, wlist, xlist = select.select(([self.socket]) + list(self.open_clients.keys()),
                                                list(self.open_clients.keys()), [], 0.03)
            for current_socket in rlist:
                # new client
                if current_socket is self.socket:
                    client, addr = self.socket.accept()
                    print(f'{addr[0]} connected!')
                    if addr[0] == "127.0.0.1":
                        addr = (("127.0.0." + str(self.count), addr[1]))
                        self.count += 1

                    threading.Thread(target=self._set_key(client, addr[0]))

                    continue

                else:
                    if current_socket in self.open_clients:
                        try:
                            data_len = int(current_socket.recv(3).decode())
                            data = current_socket.recv(data_len).decode()
                        except Exception as e:
                            print("main server in server comm" + str(e))
                            self._disconnect_client(current_socket)
                        else:
                            if data == '':
                                self._disconnect_client(current_socket)
                            else:

                                self.rcv_q.put((self.open_clients[current_socket][0], self.open_clients[current_socket][1].decrypt(data)))


    def _disconnect_client(self, client):
        '''
        gets client to
        :param client:
        :return:
        '''
        if client in self.open_clients.keys():
            print(f'{self.open_clients[client]} - disconnected')
            self.rcv_q.put((self.open_clients[client][0], "99"))
            del self.open_clients[client]

    def _find_socket_by_ip(self, ip):
        '''
        gets ip and returns the socket matched
        :param ip: ip got (string)
        :return: socket matched (socket)
        '''
        client = None
        for soc in self.open_clients.keys():
            if self.open_clients[soc][0] == ip:
                client = soc
                break
        return client

    def send(self, ip, msg):
        '''
        send msg to client
        :param ip: str
        :param msg: str
        :return:
        '''
        if self.is_running:
            client = self._find_socket_by_ip(ip)
            if client:
                msg_encrypted = self.open_clients[client][1].encrypt(msg)
                try:
                    client.send(str(len(msg_encrypted)).zfill(3).encode())
                    client.send(msg_encrypted)

                except Exception as e:
                    print('server comm - send', str(e))
                    self._disconnect_client(client)


    def sendAll(self,msg):
        '''
        send msg to everyone
        :param msg: str
        :return:
        '''
        if self.is_running:
            for client in self.open_clients.keys():
                try:
                    client.send(str(len(msg)).zfill(3).encode())
                    client.send(msg.encode())
                except Exception as e:
                    print('server comm - send', str(e))
                    self._disconnect_client(client)

    def close_server(self):
        self.is_running = False

    def is_running(self):
        return self.is_running

    def _set_key(self, socket, ip):
        """
        set key
        :param socket:
        :param ip:
        :return:
        """
        random_num = random.randint(0, self.p - 3) + 1
        personal_key = "50" + str(self.g ** random_num % self.p)
        try:
            socket.send(str(len(personal_key)).zfill(3).encode())
            socket.send(personal_key.encode())
        except Exception as e:
            print("server comm - set key ", str(e))
        try:
            data_len = int(socket.recv(3).decode())
            data = socket.recv(data_len).decode()
        except Exception as e:
            self._disconnect_client(socket)
        else:
            key = str(int(data[2:]) ** random_num % self.p)
            self.open_clients[socket] = (ip, Encryption(key))



if __name__ == '__main__':
    msg_q = queue.Queue()
    server = ServerComm(4500, msg_q)
    print(msg_q.get())
    server.send('127.0.0.1', "hi")