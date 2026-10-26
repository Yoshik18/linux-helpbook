# 10. Debug a network request one layer at a time

A request can fail before it reaches an application: name lookup, route selection, transport connection, TLS negotiation, then HTTP handling. Test from the affected client and preserve the exact hostname, port, time and error. Each check below answers one question; none alone proves end-to-end health.

The Linux examples use `ip` and `ss` from iproute2. `dig` is commonly supplied by `dnsutils`/`bind-utils`; `curl` may need installing in a disposable lab. Names and packages vary by distribution. Missing tools are not network evidence. Inspection commands do not change configuration. DNS examples can query external infrastructure; use approved names.

## 1. What name does this machine resolve?

```bash
getent ahosts example.com
```

`getent` uses the system's configured name-service path (often `/etc/hosts`, DNS, or a local resolver). Returned addresses prove that this lookup path supplied answers at that moment, not that the application uses the same resolver or can reach those addresses. No result may mean lookup failure, filtering, or no matching record.

To inspect a DNS response directly, if `dig` is installed:

```bash
dig example.com A
dig example.com AAAA
```

`A` asks for IPv4 and `AAAA` for IPv6. Read `status`, answer section, TTL, and responding server; `dig +short` is compact but hides those clues. Direct queries may bypass some system lookup behavior. A cached answer can be stale, and a DNS answer does not establish route or service health.

## 2. Which interface and route would Linux use?

```bash
ip -br address
ip route
ip route get 203.0.113.10
```

`-br` gives a compact interface/address view. `ip route` lists the main IPv4 routing table; `ip -6 route` lists IPv6. `ip route get ADDRESS` asks the kernel to resolve a destination and usually shows selected interface, source address and next hop. It does not send a packet or test the gateway. Policy routing, VPNs and network namespaces can select other paths. Do not modify routes on a remote machine as an experiment.

## 3. Is a local TCP socket listening on the expected address?

```bash
ss -lnt
ss -lnt 'sport = :8080'
```

`-l` shows listening sockets, `-n` keeps numeric addresses/ports, and `-t` selects TCP. The filter narrows the source port. `127.0.0.1:8080` is loopback-only; `0.0.0.0:8080` binds all local IPv4 addresses, subject to firewall and routing. No matching listener is evidence that this network namespace has no visible TCP listener there; permissions, UDP, another namespace or a different port are possible explanations. `ss -p` may show process names when permitted, but also exposes process details.

## 4. Test connection and application response separately

A safe reproducible lab serves only the fixture notes on loopback. From the repository root, terminal one:

```bash
source fundamentals/labs/setup.sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$LINUX_LAB/notes"
```

This requires Python 3 and an unused port. It is a teaching server, not production software; do not serve a sensitive directory. In terminal two:

```bash
curl --connect-timeout 2 --max-time 5 --fail http://127.0.0.1:8765/todo.txt
curl --connect-timeout 2 --max-time 5 --output /dev/null --write-out 'HTTP %{http_code}\n' http://127.0.0.1:8765/missing
```

The first should print fixture text; the second should report 404. `--connect-timeout` bounds connection setup; `--max-time` bounds the whole transfer; `--fail` makes HTTP error responses return a nonzero curl status. Without `--fail`, curl can return success for HTTP 404. A 404 proves an HTTP server answered this request, not that the desired resource exists. Stop only your lab server with Ctrl+C.

For an authorized HTTPS endpoint:

```bash
curl --verbose --connect-timeout 3 --max-time 10 --output /dev/null https://example.com/
```

Verbose output shows progress through resolution, connection, TLS and HTTP; it may expose URLs or headers, so review before sharing. A connection refusal differs from timeout; neither uniquely identifies the cause. Do not use `--insecure` to conceal certificate failures. `ping` tests ICMP, not TCP or HTTP. HTTPS may use HTTP/3/QUIC rather than TCP, so identify the protocol before assuming a TCP-only path.

## Practice: where does the request stop?

With the loopback server running, compare `ss` output, a successful file request and a missing-file request. Then stop the server and repeat the request. For each result, state what it proves and one alternative explanation it leaves open. Extend the investigation with `getent`, `dig`, and `ip route get` for a hostname you are allowed to query; these exercise different layers than the numeric loopback lab.

[Manual: ss](https://man7.org/linux/man-pages/man8/ss.8.html) · [ip route](https://man7.org/linux/man-pages/man8/ip-route.8.html) · [curl](https://curl.se/docs/manpage.html) · [Previous](09-packages-and-software.md) · [Index](README.md) · [Next](11-isolation-and-security.md)
