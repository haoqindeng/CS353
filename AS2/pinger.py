import socket
from threading import Thread
from sys import argv

import os
import sys
import socket
import struct
import select
import time
import ctypes

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def get_checksum(msg):
    # print(msg)
    s = 0
    for i in range(0, len(msg), 2):
        if i == len(msg) - 1:
            w = msg[i] << 8
        else:
            w = (msg[i] << 8 ) + (msg[i+1])
        s = carry_around_add(s, w)
    # print(~s & 0xffff)
    return ~s & 0xffff

# def get_checksum(source):
#     """
#     return the checksum of source
#     the sum of 16-bit binary one's complement
#     """
#     checksum = 0
#     count = (len(source) / 2) * 2
#     i = 0
#     while i < count:
#         temp = ord(source[i + 1]) * 256 + ord(source[i]) # 256 = 2^8
#         checksum = checksum + temp
#         checksum = checksum & 0xffffffff # 4,294,967,296 (2^32)
#         i = i + 2

#     if i < len(source):
#         checksum = checksum + ord(source[len(source) - 1])
#         checksum = checksum & 0xffffffff

#     # 32-bit to 16-bit
#     checksum = (checksum >> 16) + (checksum & 0xffff)
#     checksum = checksum + (checksum >> 16)
#     answer = ~checksum
#     answer = answer & 0xffff

#     # why? ans[9:16 1:8]
#     answer = answer >> 8 | (answer << 8 & 0xff00)
#     return answer
#     # recite from https://blog.csdn.net/csdn_moming/article/details/51202650

# byte_in_double = struct.calcsize("d") # C type: double
# data = (108 - byte_in_double) * "P" # any char is OK, any length is OK
# data = struct.pack("d", time.clock()) + data
# print(time.clock())
# print(data)

# checksum = 0
# ICMP_ECHO_REQUEST = 8
# ID = 1
# header = struct.pack('BBHHH', ICMP_ECHO_REQUEST, 0, checksum, ID, 1)
# print(header)

# st = '8'.encode()
# print(ord(str(st[0])))
# print(st[0])

cmd_dict = {}
it = 1
while it < len(argv):
    cmd_dict[argv[it]] = argv[it + 1]
    it += 2
# print(argv)
payload = ""
count = 10
destination = ""
logfile = ""
print(cmd_dict)
if '-p' in cmd_dict:
    payload = cmd_dict['-p']
if '-c' in cmd_dict:
    count = int(cmd_dict['-c'])
if '-d' in cmd_dict:
    destination = cmd_dict['-d']
if '-l' in cmd_dict:
    logfile = cmd_dict['-l']
# print('payload: ' + payload)
# print('count: ' + str(count))
# print('destination: ' + destination)
# print('logfile: ' + logfile)
ip = socket.gethostbyname(destination)
# print(ip)
icmp = socket.getprotobyname('icmp')
try:
    socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
except:
    print('error with opening the socket')

print('Pinging ' + destination + ' with ' + str(len(payload.encode())) + ' bytes of data ' + payload)

num = 0
ID = 0
seq = 0
pkt_loss = 0
while num < count:
    time_sent = time.time()
    # print('time sent: ' + str(time_sent))

    checksum = 0
    ICMP_ECHO_REQUEST = 8
    ID += 1
    seq += 1
    header = struct.pack('!bbHHh', ICMP_ECHO_REQUEST, 0, checksum, ID, seq)
    # print(header)
    checksum = get_checksum(header + payload.encode())
    # checksum = get_checksum(header)
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, checksum, ID, seq)
    packet = header + payload.encode()
    socket.sendto(packet, (ip, 80))
    # socket.sendto('hello'.encode(), (ip, 80))
    # receive

    start_time = 2
    start_select = time.clock()
    what_ready = select.select([socket], [], [], 3)
    if what_ready[0] == []:
        print('failed to transimit on timeout')
        num += 1
        pkt_loss += 1
        continue
    time_received = time.time()
    # print('time_received: ' + str(time_received))
    rec_packet, addr = socket.recvfrom(1024)
    icmp_header = rec_packet[20 : 28]
    ip_type, code, checksum, packet_ID, sequence = struct.unpack("!bbHHh", icmp_header)
    TTL = rec_packet[8]
    # ttl = TTL.decode()
    # print(packet_ID)
    if ip_type == 0 and packet_ID == ID:
        print('Reply from ' + destination + ':bytes=' + str(len(payload.encode())) + ' time=:' + str(int(1000 * (time_received - time_sent))) + 'ms TTL=' + str(TTL))
    else:
        print('failed to transimit on timeout')
        pkg_loss += 1

    num += 1
print('Ping statistics for ' + destination + ': Packets Sent = ' + str(count) + 
        ', Received = ' + str(count - pkt_loss) + ', Lost = ' + str(int(100 * pkt_loss / count)) + '%')