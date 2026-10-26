# 10. Debug addresses, DNS, ports and HTTP

Work from the affected client's viewpoint. The commands below do not change
routes, firewalls or DNS configuration. `ip`/`ss` require iproute2, `dig` DNS tools,
and `curl` its own package. Missing utilities are not a failed network.

## Check local interfaces and route selection

```bash
ip -br address
ip route
ip -6 route
ip route get 127.0.0.1
```

`-br` is brief output. Addresses show what is configured; routes show forwarding
choices. `route get` asks the kernel to resolve a route and source address, not
to send a packet. Policy routing can involve multiple tables. IPv6 may be disabled.
Do not change a default route while connected through the path you are changing.

## Separate name-service lookup from a DNS query

```bash
getent ahosts localhost
```

`getent` follows the configured host lookup sources, potentially `/etc/hosts`,
DNS and resolver services. For a public name you are allowed to query:

```bash
dig example.com A
dig example.com AAAA
dig +short example.com A
```

Full `dig` output includes the response status, flags, TTLs and answering resolver;
`+short` hides useful context. These requests may contact an external resolver.
A DNS answer does not prove the service accepts connections, and applications
with their own resolver can behave differently from `getent`.

## Find a listening port and its address

```bash
ss -lnt
ss -lntp
ss -lnt 'sport = :8765'
```

`-l` selects listeners, `-n` numeric endpoints, `-t` TCP and `-p` process details
when permitted. A listener on `127.0.0.1` accepts loopback traffic; `0.0.0.0`
binds all local IPv4 addresses but does not bypass firewalls. IPv6 wildcard
behavior is configurable. Several connections can share one server port because
the remote address/port also identifies a TCP connection.

## Start a service you can safely break

From the repository root in terminal one:

```bash
source fundamentals/labs/setup.sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$LINUX_LAB/notes"
```

This serves only fictional notes on loopback. Use another unused port if needed.
Do not serve your home directory. In terminal two:

```bash
curl --fail --max-time 3 http://127.0.0.1:8765/todo.txt
curl --max-time 3 --output /dev/null --write-out 'HTTP %{http_code}\n' http://127.0.0.1:8765/missing
```

Expect the three todo lines, then HTTP 404. Plain curl can return zero for an
HTTP error; `--fail` makes this 404 return status 22. Stop your server with Ctrl+C
in terminal one. Python's small server is a lab tool, not a production service.

## Tell connection, TLS and HTTP failures apart

For an endpoint you are authorized to contact, a verbose curl request shows the
stages. For example, this contacts a public demonstration domain:

```bash
curl --verbose --connect-timeout 3 --max-time 10 https://example.com/ -o /dev/null
```

Look for name resolution, connection, TLS negotiation and the HTTP response.
Do not use `--insecure` as a certificate repair. A refused connection often means
no listener or active rejection; a timeout has several possible causes. Ping
checks ICMP, not whether an HTTP/TCP application works. HTTP/3 uses QUIC/UDP and
does not follow the HTTPS-over-TCP sequence.

## Practice

With the local server running, identify its listening address and request one
existing and one missing file. Explain what a 404 proves that a timeout does not.

<details>
<summary>One answer</summary>

```bash
ss -lnt 'sport = :8765'
curl --fail --max-time 3 http://127.0.0.1:8765/todo.txt
curl --fail --max-time 3 http://127.0.0.1:8765/missing
```

</details>

[Manual: ss](https://man7.org/linux/man-pages/man8/ss.8.html)
· [ip route](https://man7.org/linux/man-pages/man8/ip-route.8.html)
· [curl](https://curl.se/docs/manpage.html)
· [HTTP/3](https://www.rfc-editor.org/rfc/rfc9114.html)
· [Previous](09-packages-and-software.md) · [Index](README.md) · [Next](11-isolation-and-security.md)
