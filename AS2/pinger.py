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
    print(msg)
    s = 0
    for i in range(0, len(msg), 2):
        print(type(msg[i]))
        if i == len(msg) - 1:
            w = msg[i] << 8
        else:
            w = (msg[i] << 8 ) + (msg[i+1])
        s = carry_around_add(s, w)
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
print(argv)
payload = "hello"
count = 10
destination = ""
logfile = ""
if '-p' in cmd_dict:
    payload = cmd_dict['-p']
if '-c' in cmd_dict:
    count = cmd_dict['-c']
if '-d' in cmd_dict:
    destination = cmd_dict['-d']
if '-l' in cmd_dict:
    logfile = cmd_dict['-l']
print('payload: ' + payload)
ip = socket.gethostbyname('google.com')
print(ip)
icmp = socket.getprotobyname('icmp')
try:
    socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
except:
    print('error with opening the socket')

time_sent = time.time()
print('time sent: ' + str(time_sent))

checksum = 0
ICMP_ECHO_REQUEST = 8
ID = 1
header = struct.pack('!bbHHh', ICMP_ECHO_REQUEST, 0, checksum, ID, 1)
# print(header)
checksum = get_checksum(header + payload.encode())
# checksum = get_checksum(header)
header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, checksum, ID, 1)
packet = header + payload.encode()
socket.sendto(packet, (ip, 80))
# socket.sendto('hello'.encode(), (ip, 80))
# receive

start_time = 2
start_select = time.clock()
what_ready = select.select([socket], [], [])
print('line 115')
time_received = time.time()
print('time_received: ' + str(time_received))
rec_packet, addr = socket.recvfrom(1024)
icmp_header = rec_packet[20 : 28]
ip_type, code, checksum, packet_ID, sequence = struct.unpack("!bbHHh", icmp_header)
print(packet_ID)
if ip_type != 8 and packet_ID == ID:
    print('RTT is: ' + str(time_received - time_sent))