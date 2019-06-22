import socket
from general import *
from networking.ethernet import Ethernet
from networking.ipv4 import IPv4
from networking.ipv6 import IPv6
from networking.icmp import ICMP
from networking.tcp import TCP
from networking.udp import UDP
from networking.pcap import Pcap
from networking.http import HTTP
import sys
import json
import time
import asyncio

TAB_1 = '\t - '
TAB_2 = '\t\t - '
TAB_3 = '\t\t\t - '
TAB_4 = '\t\t\t\t - '

DATA_TAB_1 = '\t   '
DATA_TAB_2 = '\t\t   '
DATA_TAB_3 = '\t\t\t   '
DATA_TAB_4 = '\t\t\t\t   '



def showIpv4(ipv4):
    print(TAB_1 + 'IPv4 Packet:')
    print(TAB_2 + 'Version: {}, Header Length: {}, TTL: {},'.format(ipv4.version, ipv4.header_length, ipv4.ttl))
    print(TAB_2 + 'Protocol: {}, Source: {}, Target: {}'.format(ipv4.proto, ipv4.src, ipv4.target))

    # ICMP
    if ipv4.proto == 1:
        icmp = ICMP(ipv4.data)
        print(TAB_1 + 'ICMP Packet:')
        print(TAB_2 + 'Type: {}, Code: {}, Checksum: {},'.format(icmp.type, icmp.code, icmp.checksum))
        print(TAB_2 + 'ICMP Data:')
        print(format_multi_line(DATA_TAB_3, icmp.data))

    # TCP
    elif ipv4.proto == 6:
        tcp = TCP(ipv4.data)
        print(TAB_1 + 'TCP Segment:')
        print(TAB_2 + 'Source Port: {}, Destination Port: {}'.format(tcp.src_port, tcp.dest_port))
        print(TAB_2 + 'Sequence: {}, Acknowledgment: {}'.format(tcp.sequence, tcp.acknowledgment))
        print(TAB_2 + 'Flags:')
        print(TAB_3 + 'URG: {}, ACK: {}, PSH: {}'.format(tcp.flag_urg, tcp.flag_ack, tcp.flag_psh))
        print(TAB_3 + 'RST: {}, SYN: {}, FIN:{}'.format(tcp.flag_rst, tcp.flag_syn, tcp.flag_fin))

        if len(tcp.data) > 0:

            # HTTP
            if tcp.src_port == 80 or tcp.dest_port == 80:
                print(TAB_2 + 'HTTP Data:')
                try:
                    http = HTTP(tcp.data)
                    http_info = str(http.data).split('\n')
                    for line in http_info:
                        print(DATA_TAB_3 + str(line))
                except:
                    print(format_multi_line(DATA_TAB_3, tcp.data))
            else:
                print(TAB_2 + 'TCP Data:')
                print(format_multi_line(DATA_TAB_3, tcp.data))

    # UDP
    elif ipv4.proto == 17:
        udp = UDP(ipv4.data)
        print(TAB_1 + 'UDP Segment:')
        print(TAB_2 + 'Source Port: {}, Destination Port: {}, Length: {}'.format(udp.src_port, udp.dest_port, udp.size))

    # Other IPv4
    else:
        print(TAB_1 + 'Other IPv4 Data:')
        print(format_multi_line(DATA_TAB_2, ipv4.data))

fila = []

def show():
    filter = ['ipv4', 'ipv6', 'other']
    idx = 0
    if len(sys.argv)>1:
        filter = sys.argv[1:]
    print("[s] Filter: {}".format(filter))
    global fila
    while True:
        print("[s] {} {}".format(idx, len(fila)))  
        if idx >= len(fila):
            time.sleep( 0.5 )
            continue
        eth = fila[idx]
        idx = idx+1
        # IPv4
        if eth.prototype == 2048 and 'ipv4' in filter:
            print(TAB_1 + 'IPv4 Packet:')
            print( eth.toJSON())
        elif eth.prototype == 34525 and 'ipv6' in filter:
            print(TAB_1 + 'IPv6 Packet:')
            print( eth.toJSON())
        elif  'other' in filter:
            if  eth.prototype == 2054:
                print("ARP protocol:")  
            print("Prototype: {}".format(eth.prototype))
            print( eth.toJSON())

        time.sleep( 0.1)



def read():
    pcap = Pcap('capture.pcap')
    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    global fila
    while True:
        raw_data, addr = conn.recvfrom(65535)
        pcap.write(raw_data)
        eth = Ethernet(raw_data)

        fila.append(eth)  
        print("[r] fila:{}".format(len(fila)))  
        time.sleep( 0.3)

    pcap.close()

from multiprocessing import Process, Pool
import threading

def main():  
    global fila
    x = threading.Thread(target=read)
    x.start()

    y = threading.Thread(target=show)
    y.start()

main()
