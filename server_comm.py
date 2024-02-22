import select
import socket
import threading
import queue
import  random
from encryptionClass import Encryption


class ServerComm:

    def __init__(self, port, rcv_q):
        self.port = port
        self.rcv_q = rcv_q
        self.socket = socket.socket()
        # socket: ip
        self.open_clients = {}
        self.is_running = False
        self.count = 1
        # self.encryption = {} # ip: encryption
        # self.g = 6269
        # self.p = 1433
        # self.personal_key = random.randint(self.p-3)+1
        threading.Thread(target=self._main_loop).start()

    def _main_loop(self):
        self.socket.bind(("0.0.0.0", self.port))
        self.socket.listen(3)
        self.is_running = True
        while self.is_running:
            rlist, wlist, xlist = select.select(([self.socket]) + list(self.open_clients.keys()),
                                                list(self.open_clients.keys()), [], 0.03)
            # new client
            for current_socket in rlist:
                if current_socket is self.socket:
                    client, addr = self.socket.accept()
                    print(f'{addr[0]} connected!')
                    if addr[0] == "127.0.0.1":
                        addr = (("127.0.0." + str(self.count), addr[1]))
                        self.count += 1
                    self.open_clients[client] = addr[0]
                    # try:
                    #     client.send(f"07{self.g ** self.personal_key % self.p}".encode())
                    # except Exception as e:
                    #     self._disconnect_client(client)
                    continue


                else:
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
                            # if not adrr[0] in self.encryption:
                            #     self.recv_q.put(data)
                            # else:
                            #     self.recv_q.put(self.encryption[adrr[0]].decryption(data)) # decrypted data

                            self.rcv_q.put((self.open_clients[current_socket], data))


    def _disconnect_client(self, client):
        '''
        gets client to
        :param client:
        :return:
        '''
        if client in self.open_clients.keys():
            print(f'{self.open_clients[client]} - disconnected')
            del self.open_clients[client]

    def _find_socket_by_ip(self, ip):
        '''
        gets ip and returns the socket matched
        :param ip: ip got (string)
        :return: socket matched (socket)
        '''
        client = None
        for soc in self.open_clients.keys():
            if self.open_clients[soc] == ip:
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
                try:
                    client.send(str(len(msg)).zfill(3).encode())
                    client.send(msg.encode())
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
        return self.is_running()


if __name__ == '__main__':
    msg_q = queue.Queue()
    server = ServerComm(10000, msg_q)
