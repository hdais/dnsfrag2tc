# `dnsfrag2tc` - NFQUEUE function which forces DNS clients to TCP query upon receiving fragmented DNS responses.

This NFQUEUE function _captures_ **fragmented** UDP DNS response and _replaces_ it with **TC=1** responses. DNS clients will retry DNS query in TCP mode.

## Usage
```
 iptables -t raw -A PREROUTING -p udp --sport 53 -j NFQUEUE --queue-num 12345
 ./dnsfrag2tc.py 12345
```
Do not forget to delete this iptables rule (`iptables -t raw -F`) after dnsfrag2tc exits. Or all DNS messages will be droped.

## Example
### Before
Without `dnsfrag2tc`, we get large fragmented UDP response.
<pre>
$ <b>dig @199.6.0.30 isc.org MX +dnssec +ignore +bufsize=4096</b>

;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 3710
;; flags: qr aa rd; QUERY: 1, ANSWER: 4, AUTHORITY: 6, ADDITIONAL: 27
; <<>> DiG 9.10.3-P4-Ubuntu <<>> @199.6.0.30 isc.org MX +dnssec +ignore

;; <b>MSG SIZE  rcvd: 3251</b>
</pre>

### After
With `dnsfrag2tc`, `dig` makes queryin TCP mode.
<pre>
$ <b>dig @199.6.0.30 isc.org MX +dnssec +bufsize=4096</b>

;; <b><u>Truncated, retrying in TCP mode.</u></b>

; <<>> DiG 9.10.3-P4-Ubuntu <<>> @199.6.0.30 isc.org MX +dnssec
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 28547
;; flags: qr aa rd; QUERY: 1, ANSWER: 4, AUTHORITY: 6, ADDITIONAL: 27

;; MSG SIZE  rcvd: 3251
</pre>
... This is because we got **TC=1** response (actually dnsfrag2tc genarated this).
<pre>
$ <b>dig @199.6.0.30 isc.org MX +dnssec +ignore +bufsize=4096</b>

; <<>> DiG 9.10.3-P4-Ubuntu <<>> @199.6.0.30 isc.org MX +dnssec +ignore
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 38868
;; flags: qr <b>tc</b> rd; QUERY: 0, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 0

;; <b>MSG SIZE  rcvd: 12</b>
</pre>
`dnsfrag2tc` won't touch non-fragmented responses.
<pre>
$ <b>dig @8.8.8.8 www.google.com</b>
; <<>> DiG 9.10.3-P4-Ubuntu <<>> @8.8.8.8 www.google.com
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 29815
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; MSG SIZE  rcvd: 59
</pre>

## Requirements
- [Python3](https://python.org/)
- [Scapy](https://scapy.net/)
- [NetfilterQueue](https://pypi.org/project/NetfilterQueue/)
