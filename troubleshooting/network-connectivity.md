# A service is unreachable: test one layer at a time

Write down the exact hostname, port, protocol, client and error before changing
anything. A timeout, refused connection, DNS failure and HTTP error are different
observations. Compare from the affected client, not only from the server.

## 1. Check name resolution

```bash
getent ahosts example.com
```

On Linux with glibc/NSS tools, `getent` follows configured name-service sources,
which can include `/etc/hosts` and DNS. It is not available in every minimal image.
If installed, `dig example.com A` and `dig example.com AAAA` query DNS rather than
reproducing every application resolver path. A successful DNS answer does not
prove TCP, TLS or application health. Avoid treating a cached answer as evidence
that every resolver sees a recent change.

## 2. Check the server's listening socket

On the server, with iproute2 installed:

```bash
ss -lnt
```

Check the port and local address. A listener bound to `127.0.0.1` is reachable
through IPv4 loopback, not directly through the host's external address. `0.0.0.0`
means all local IPv4 addresses, but does not bypass firewalls. IPv6 behavior and
dual-stack acceptance depend on configuration. `ss -lntp` can add process details
when permissions allow.

A listener is not proof the application can serve requests. If the client sees
connection refused, a common cause is no listener on that address/port; an active
network rejection can produce a similar result. A timeout can involve routing,
filtering, overload or an unresponsive peer. Do not label every timeout a firewall
problem.

## 3. Inspect the HTTP/TLS path

For an endpoint you are allowed to contact:

```bash
curl --verbose --connect-timeout 3 --max-time 10 https://example.com/ -o /dev/null
```

Use the output to separate resolution, connection, TLS negotiation and HTTP
response. Plain `curl` can return exit status zero for an HTTP 404 or 500; use
`--fail` if an HTTP error should fail a script. Do not add `--insecure` as a TLS
fix. Check certificate identity, trust, expiry and the client clock instead.
Verbose traces can expose headers or credentials; redact before sharing.

Ping tests ICMP reachability. It does not test whether an HTTP/TCP service works,
and ICMP filtering can make ping fail while the application remains reachable.

## Try it locally

This lab needs Python 3 and curl. It serves only a newly created temporary
folder, bound to loopback. Do not serve your home directory or credentials.

Terminal one:

```bash
lab=$(mktemp -d) || exit 1
printf 'hello from a local lab\n' > "$lab/index.html"
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$lab"
```

Terminal two:

```bash
curl --fail --max-time 3 http://127.0.0.1:8765/
ss -lnt
```

Expect the text from `index.html` and a loopback listener on port 8765. If the port
is occupied, choose another unused port in both terminals. Stop your lab server
with Ctrl+C in terminal one. Python's simple server is for this lab, not production.
The HTTP exchange can be tested separately even when `ss` is not installed.

## Interview takeaway

- Why can ping work while an HTTPS request fails?
- Why does a service work locally but not from another host?

## Further reading

- [`ss(8)`](https://man7.org/linux/man-pages/man8/ss.8.html)
- [`getent(1)`](https://man7.org/linux/man-pages/man1/getent.1.html)
- [curl manual](https://curl.se/docs/manpage.html)
- [Python HTTP server](https://docs.python.org/3/library/http.server.html)

[Back to the learning path](../README.md)
