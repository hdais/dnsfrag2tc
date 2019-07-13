#!/usr/bin/env python3

# NFQUEUE function which captures fragmented DNS/UDP/IPv4 response
# and replaces it with TC=1 response

# Requires Python3, Scapy and NetfilterQueue.

# Usage:
#  iptables -t raw -A PREROUTING -p udp --sport 53 -j NFQUEUE --queue-num 12345 
#  ./dnsfrag2tc.py 12345
# don't forget to delete this iptables rule after dnsfrag2tc exits...

from netfilterqueue import NetfilterQueue
from scapy.all import *
import sys

def process(pkt):
	packet = IP(pkt.get_payload())
	# is UDP datagram's first fragment?
	if packet.flags & 0x1 and packet.frag == 0 and packet.proto == 0x11:
		# is source port == 53 (DNS response?)
		if packet[UDP].sport == 53:
			dnsmsg = bytes(packet[UDP].payload)
			if len(dnsmsg) < 12:
				return
			# is a resnponse ?
			if dnsmsg[2] & 0x80 == 0:
				pkt.accept()
				return
			# opcode ? 
			if dnsmsg[2] & 0x78 != 0:
				pkt.accept()
				return
			# so this is fragmented DNS response.
			id = dnsmsg[0] * 256 + dnsmsg[1]
			pkt.set_payload(bytes(gentc(packet, id)))
			pkt.accept()
			return
	pkt.accept()

def gentc(packet,id):
	ip = IP()
	udp = UDP()
	ip.src = packet[IP].src
	ip.dst = packet[IP].dst
	udp.sport = packet[UDP].sport
	udp.dport = packet[UDP].dport
	dns = DNS(id=id, qr=1, tc=1)
	return ip/udp/dns

def main():
	nfqueue = NetfilterQueue()
	nfqueue.bind(int(sys.argv[1]), process)
	try:
		nfqueue.run()
	except KeyboardInterrupt:
		print('')
	nfqueue.unbind()

if __name__ == '__main__':
	main()
