import socket
from threading import Thread 
from sys import argv

# for sending to another server
class SubTcpThreadSendTo(Thread):
    def __init__(self, conn, addr): 
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.data = ''
 
    def run(self): 
        while True : 
            if self.data != '':
                self.conn.sendall(self.data.encode())
                self.data = ''

# Multithreaded Python server : TCP Server Socket Thread Pool
class SubTcpThread(Thread):
    def __init__(self, conn, addr): 
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
 
    def run(self): 
        global g_var
        global s
        global client_thread_pool
        global name_thread_dict
        global f
        while True:
            data = self.conn.recv(1024) 
            print(data.decode())
            msg = data.decode().split(' ')
            if msg[0] == 'sendto':
                g_var = g_var + 1
                # send through udp
                # recvfrom_name = ''
                # for th in client_thread_pool:
                #     if th.addr == self.addr:
                #         recvfrom_name = th.name
                #         break
                recvfrom_name = msg[-1]
                msg = msg[:-1]
                sendto_name = msg[1]
                content = ''
                # locally found receiver
                if sendto_name in name_thread_dict:
                    sendto_thread = name_thread_dict[sendto_name]

                    
                    it = 2
                    while it < len(msg):
                        content = content + msg[it] + ' '
                        it += 1
                    content = content[:-1]

                    sendto_thread.data = 'recvfrom ' + recvfrom_name + ' ' + content
                    f.write('sendto ' + sendto_name + ' from ' + recvfrom_name + ' ' + content + '\n')
                    f.write('recvfrom ' + recvfrom_name + ' to ' + sendto_name + ' ' + content + '\n')

                else:
                    for th in server_thread_pool:
                        if th.addr != self.addr:
                            th.data = data.decode()
                            print('send to overley ' + data.decode())
                    f.write('sendto ' + sendto_name + ' from ' + recvfrom_name + ' ' + content + '\n')
                    f.write(sendto_name + ' not registered with server\n')
                    f.write('recvfrom ' + recvfrom_name + ' to ' + sendto_name + ' ' + content + '\n')
                   

# for listening from other servers
class TcpThread(Thread):
    def __init__(self, socket, addr): 
        Thread.__init__(self)
        self.socket = socket
        self.addr = addr
 
    def run(self): 
        global server_thread_pool
        global f
        while True : 
            self.socket.listen(5)
            conn, addr = self.socket.accept()
            print('connection established')
            f.write('server joined overlay from host ' + addr[0] + ' port ' + str(addr[1]) + '\n')
            new_thread = SubTcpThread(conn, addr)
            new_thread.daemon = True
            new_thread.start()
            # msg = conn.recv(1024)
            new_thread2 = SubTcpThreadSendTo(conn, addr)
            new_thread2.daemon = True
            server_thread_pool.append(new_thread2)
            new_thread2.start()


# for sending to another server
class TcpThread2(Thread):
    def __init__(self, socket, addr): 
        Thread.__init__(self)
        self.socket = socket
        self.addr = addr
        self.data = ''
 
    def run(self): 
        while True : 
            if self.data != '':
                self.socket.sendall(self.data.encode())
                self.data = ''

class ClientThread(Thread): 
 
    def __init__(self, socket, addr, data, name): 
        Thread.__init__(self)
        self.socket = socket
        self.addr = addr
        self.data = data
        self.name = name
 
    def run(self): 
        while True : 
            if self.data != '':
                self.socket.sendto(self.data.encode(), self.addr)
                print('sendto ' + self.name + ' ' + self.data)
              
                self.data = ''



cmd_dict = {}

it = 1
while it < len(argv):
    cmd_dict[argv[it]] = argv[it + 1]
    it += 2



name_thread_dict = {}
client_thread_pool = []
server_thread_pool = []
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


host = '127.0.0.1'
port = int(cmd_dict['-p'])
file_name = cmd_dict['-l']
f = open(file_name, 'w')
f.write('server started on ' + host + ' at port ' + str(port) + '...\n')
print('server started...')
overlayport = -1
serveroverlayIP = -1
serveroverlayport = -1
if '-o' in cmd_dict:
    overlayport = int(cmd_dict['-o'])
    f.write('server overlay started at port ' + str(overlayport) + '\n')
if '-s' in cmd_dict:
    serveroverlayIP = cmd_dict['-s']
if '-t' in cmd_dict:
    serveroverlayport = int(cmd_dict['-t'])

# print(host)
# print(port)
# print(overlayport)
# print(serveroverlayIP)
# print(serveroverlayport)

data2 = 'hello_back'.encode()

# TCP part
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if overlayport != -1:

    addr = (host, overlayport)
    tcp_socket.bind(addr)
    new_thread = TcpThread(tcp_socket, addr)
    new_thread.daemon = True
    new_thread.start()
    # server_thread_pool.append(new_thread)

# reach_out = False
tcp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if serveroverlayIP != -1 and serveroverlayport != -1:
    # reach_out = True
    addr = (host, serveroverlayport)
    tcp_socket2.connect(addr)
    # lllllllll;l
    # t = 'hello'
    # tcp_socket2.sendall(t.encode())
    # lllllllllll
    new_thread = TcpThread2(tcp_socket2, addr)
    new_thread.daemon = True
    server_thread_pool.append(new_thread)
    new_thread.start()

    new_thread2 = SubTcpThread(tcp_socket2, addr)
    new_thread2.daemon = True
    new_thread2.start()


# udp part
g_var = 10
s.bind((host, port))


try:

    while True:
        data, addr = s.recvfrom(1024)
        msg = data.decode().split()
        if msg[0] == 'register':
            client_name = msg[1]
            if client_name not in name_thread_dict:
                new_thread = ClientThread(s, addr, '', client_name)
                new_thread.daemon = True
                new_thread.data = 'welcome ' + client_name
                client_thread_pool.append(new_thread)
                name_thread_dict[client_name] = new_thread
                new_thread.start()
                # logfile
                f.write('client connection from host ' + addr[0] + ' port ' + str(addr[1]) + '\n')
                f.write('received register ' + client_name + ' from host ' + addr[0] + ' port ' + str(addr[1]) + '\n')
        elif msg[0] == 'exit':
            recvfrom_name = ''
            for th in client_thread_pool:
                if th.addr == addr:
                    recvfrom_name = th.name
                    break
            client_thread = name_thread_dict[recvfrom_name]
            client_thread.data = 'exit'

            # client_thread.join()
            # client_thread_pool.remove(name_thread_dict[recvfrom_name])
            # del name_thread_dict[client_name]
        elif msg[0] == 'sendto':
            recvfrom_name = ''
            for th in client_thread_pool:
                if th.addr == addr:
                    recvfrom_name = th.name
                    break
            sendto_name = msg[1]
            # locally found receiver

            content = ''
            it = 2
            while it < len(msg):
                content = content + msg[it] + ' '
                it += 1
            content = content[:-1]
            if sendto_name in name_thread_dict:
                sendto_thread = name_thread_dict[sendto_name]

                

                sendto_thread.data = 'recvfrom ' + recvfrom_name + ' ' + content
                f.write('sendto ' + sendto_name + ' from ' + recvfrom_name + ' ' + content + '\n')
                f.write('recvfrom ' + recvfrom_name + ' to ' + sendto_name + ' ' + content + '\n')
            else:
                # forward to other server
                # if reach_out == True:
                for th in server_thread_pool:
                    th.data = data.decode() + ' ' + recvfrom_name
                    print('send to another server...')
                f.write('sendto ' + sendto_name + ' from ' + recvfrom_name + ' ' + content + '\n')
                f.write(sendto_name + ' not registered with server\n')
                f.write('sending message to overlay ' + content + '\n')
                # f.write('recvfrom ' + recvfrom_name + ' to ' + sendto_name + ' ' + content + '\n')
            # print(name_thread_dict)
except:
    f.write('terminating server...\n')
    f.close()