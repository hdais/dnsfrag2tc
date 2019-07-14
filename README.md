# `dnsfrag2tc` - forcing DNS clients to retry in TCP mode on fragmented UDP response received

This NFQUEUE function _captures_ **fragmented** UDP DNS response and _replaces_ it with **TC=1** responses. DNS clients will retry DNS query in TCP mode.

## Usage
```
 iptables -t raw -A PREROUTING -p udp --sport 53 -j NFQUEUE --queue-num 1 --queue-bypass
 ./dnsfrag2tc.py 1
```
## Requirements
- [Python3](https://python.org/)
- [Scapy](https://scapy.net/)
- [NetfilterQueue](https://pypi.org/project/NetfilterQueue/)

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
If `dnsfrag2tc` enabled, `dig` does query in TCP mode.
<pre>
$ <b>dig @199.6.0.30 isc.org MX +dnssec +bufsize=4096</b>

;; <b><u>Truncated, retrying in TCP mode.</u></b>

; <<>> DiG 9.10.3-P4-Ubuntu <<>> @199.6.0.30 isc.org MX +dnssec
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 28547
;; flags: qr aa rd; QUERY: 1, ANSWER: 4, AUTHORITY: 6, ADDITIONAL: 27

;; MSG SIZE  rcvd: 3251
</pre>
... This is because we got **TC=1** response which dnsfrag2tc generated.
<pre>
$ dig @199.6.0.30 isc.org MX +dnssec +ignore +bufsize=4096

; <<>> DiG 9.10.3-P4-Ubuntu <<>> @199.6.0.30 isc.org MX +dnssec +ignore
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 38868
;; flags: qr <b>tc</b> rd; QUERY: 0, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 0

;; MSG SIZE  rcvd: 12
</pre>
`dnsfrag2tc` doesn't touch non-fragmented responses.
<pre>
$ <b>dig @8.8.8.8 www.google.com</b>

; <<>> DiG 9.10.3-P4-Ubuntu <<>> @8.8.8.8 www.google.com
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 29815
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; MSG SIZE  rcvd: 59
</pre>
