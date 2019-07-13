# `dnsfrag2tc` - NFQUEUE function which forces DNS clients to TCP query upon receiving fragmented DNS responses.

This NFQUEUE function captures _fragmented_ DNS/UDP/IPv4 response and _replaces_ it with TC=1 responses. DNS clents will retry DNS query via TCP.

## Usage
```
 iptables -t raw -A PREROUTING -p udp --sport 53 -j NFQUEUE --queue-num 12345
 ./dnsfrag2tc.py 12345
```
Do not forget to delete this iptables rule (`iptables -t raw -F`) after dnsfrag2tc exits. Or all DNS messages will be droped.

## Example
### Before
Without `dnsfrag2tc`, dig gets large fragmented UDP response.
<pre>
$ <b>dig @199.6.0.30 isc.org MX +dnssec +ignore +bufsize=4096</b>

;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 3710
;; flags: qr aa rd; QUERY: 1, ANSWER: 4, AUTHORITY: 6, ADDITIONAL: 27
; <<>> DiG 9.10.3-P4-Ubuntu <<>> @199.6.0.30 isc.org MX +dnssec +ignore

;; <b>MSG SIZE  rcvd: 3251</b>
</pre>

### After
With `dnsfrag2tc,` we got TC=1 response (actually dnsfrag2tc genarated this).
<pre>
$ dig @199.6.0.30 isc.org MX +dnssec +ignore +bufsize=4096

; <<>> DiG 9.10.3-P4-Ubuntu <<>> @199.6.0.30 isc.org MX +dnssec +ignore
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 38868
;; flags: qr tc rd; QUERY: 0, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 0

;; <b>MSG SIZE  rcvd: 12</b>
</pre>

dig retries in TCP mode.
<pre>
$ dig @199.6.0.30 isc.org MX +dnssec +bufsize=4096

;; <b><u>Truncated, retrying in TCP mode.</u></b>

; <<>> DiG 9.10.3-P4-Ubuntu <<>> @199.6.0.30 isc.org MX +dnssec
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 28547
;; flags: qr aa rd; QUERY: 1, ANSWER: 4, AUTHORITY: 6, ADDITIONAL: 27

;; MSG SIZE  rcvd: 3251
</pre>

## Requirements
- [Python3](https://python.org/)
- [Scapy](https://scapy.net/)
- [NetfilterQueue](https://pypi.org/project/NetfilterQueue/)
