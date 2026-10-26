# 9. Networking from the command line

[Contents](../README.md) | [Previous: storage](08-storage.md) | [Next: services](10-services.md)

A network request passes through several layers: local interface configuration, routing, name resolution when a hostname is used, transport and the application protocol. A failure at one layer does not establish that every other layer is broken. Test one question at a time and avoid changing network settings during diagnosis.

## Inspect interface addresses

```bash
ip address show
```

`ip address` displays addresses attached to network interfaces. `show` requests the current state without changing it. Look for the interface name, whether it is administratively up, and its assigned addresses. Loopback addresses such as `127.0.0.1` are local to the host. An address does not prove that a route or remote service works.

## Inspect routes

```bash
ip route show
```

This displays IPv4 routing entries. A default route is the path used when no more specific route matches. The output can vary in containers, VPNs and policy-routing setups. For IPv6, use `ip -6 route show`. Reading routes does not test packet delivery.

## Test name resolution

```bash
getent ahosts example.com
```

On glibc-based systems, `getent` asks the system name-service configuration for addresses associated with the name. The result may come from DNS, local files or another configured source. If it returns no address, inspect the resolver configuration and test with an approved known hostname. Do not assume every distribution uses the same resolver stack.

## Test an application endpoint

```bash
curl -I --max-time 5 https://example.com/
```

`curl` requests the response headers with `-I`; `--max-time 5` limits the total transfer time to five seconds. The command makes a network request to the named external service. A response establishes that this particular request reached an HTTP-speaking endpoint and returned headers; it does not prove every path, port or application function works. A proxy, TLS inspection, firewall or remote policy may affect the result. Use only endpoints you are allowed to contact.

An HTTP status such as `404` or `500` still means the server returned an HTTP response. It is different from a DNS error, connection timeout or TLS failure. Read the error message and status separately.

## Inspect listening sockets

```bash
ss -lnt
```

On Linux, `ss` displays socket information. `-l` selects listening sockets, `-n` keeps numeric addresses and ports, and `-t` selects TCP. A listening socket means a process has opened a local endpoint; it does not prove the application is healthy or reachable through a firewall. UDP sockets require a different selection, such as `-u`.

## Common confusion

- An interface having an address does not prove it can reach a destination.
- DNS success does not prove a TCP connection or application response.
- A returned HTTP error is different from a transport failure.
- A listening socket is local state, not a test from another machine.
- `ping` may be blocked even when application traffic works; lack of a ping reply is not proof all connectivity is down.

## Further reading

- [iproute2 documentation](https://www.kernel.org/pub/linux/utils/net/iproute2/)
- [Linux man-pages: ip(7)](https://man7.org/linux/man-pages/man7/ip.7.html)
- [curl manual](https://curl.se/docs/manpage.html)
- [Linux man-pages: socket(7)](https://man7.org/linux/man-pages/man7/socket.7.html)
