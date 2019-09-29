import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

host = '127.0.0.1'
port = 8080

data2 = 'hello_back'.encode()

s.bind((host, port))
# s.listen()
# conn, addr = s.accept()

# print('connected by ' + str(addr))
while True:
    data, addr = s.recvfrom(1024)
    
    print ("received data: " + data.decode())
    print(addr)
    s.sendto(data2, addr)
    if data.decode() == 'hello': 
        print('n0o data')
        break
s.close()