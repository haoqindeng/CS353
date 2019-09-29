import socket
from threading import Thread
from sys import argv

class ClientThread(Thread):
    def __init__(self, ip, socket, f, client_name):
        Thread.__init__(self)
        self.ip = ip
        self.socket = socket
        self.f = f
        self.client_name = client_name
        print('new thread initialized')

    def run(self):
        reply = 'reply'.encode()
        while True:
            data, addr = s.recvfrom(1024)
            print ("received data: " + data.decode())
            print('waiting for messages...')
            # f.write(data.decode() + '\n')
            message = data.decode().split(' ')
            msg_type = message[0]
            if msg_type == 'welcome':
                self.f.writelines('received welcome\n')
            elif msg_type == 'exit':
                print(self.client_name + ' exit')
                self.f.writelines('terminating client\n')
                break
            else:
                self.f.writelines(data.decode() + '\n')
            # self.socket.sendto(reply, addr)

# main program
print(argv)
file_name = argv[6]
# print(file_name)
client_name = argv[8]
f = open(file_name, 'w')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

host = argv[2]
# port = int(argv[4])
port = int(argv[4])
print(str(port))

addr = (host, port)
print(addr)
# s.sendto(data, (host, port))



register_msg = 'register ' + client_name
s.sendto(register_msg.encode(), addr)
f.write('connecting to the server ' + str(host) + ' at port ' + str(port) + '\n')
f.write('sending register message ' + client_name + '\n')

listen_thread = ClientThread(addr, s, f, client_name)
listen_thread.start()

while True:
    input_value = input('plelase enter: ')
    msg_type = input_value.split(' ')
    if input_value == 'exit':
        print('must terminate')
        s.sendto(str(input_value).encode(), addr)
        listen_thread.join()
        break
    else:
        f.write(input_value + '\n')

    s.sendto(str(input_value).encode(), addr)
    
    
s.close()

f.close()