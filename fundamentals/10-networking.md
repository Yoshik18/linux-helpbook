# 10. Networking

[Previous: Packages and software](09-packages-and-software.md) · [Index](README.md) · [Next: Isolation and security](11-isolation-and-security.md)

## Follow the request through separate mechanisms

An interface is a network attachment: a physical device, virtual Ethernet pair,
bridge or loopback device. IP addresses belong to interfaces; one interface can
have several addresses. A prefix describes the network portion of an address,
not a guarantee that another machine is reachable. [ip-address.8](https://man7.org/linux/man-pages/man8/ip-address.8.html)

Routes tell the kernel where to send traffic. In a routing table, more-specific
matching prefixes generally win; a default route handles destinations without
a more-specific match. Policy rules can select different tables, so one printed
default route is not a complete explanation of every application's path. [ip-route.8](https://man7.org/linux/man-pages/man8/ip-route.8.html)

Name resolution happens before an ordinary hostname-based connection. DNS is
one possible source. With glibc, Name Service Switch (NSS) configuration decides
which sources to consult, potentially including `/etc/hosts`, DNS and resolver
services. Applications using their own resolver may behave differently. [nsswitch.conf.5](https://man7.org/linux/man-pages/man5/nsswitch.conf.5.html)

## Sockets turn addresses into conversations

A socket is a kernel communication endpoint exposed to a process through a file
descriptor. TCP uses IP addresses plus ports. Within a network namespace, an
established TCP connection is distinguished by local address, local port,
remote address and remote port; including the protocol gives the familiar
five-tuple. Many clients can therefore share one server listening port without
sharing the same connection.

The TCP handshake establishes transport state, not application health. For
HTTPS over TCP, TLS negotiation follows connection establishment and adds encryption
and peer authentication. Certificate trust, hostname matching and application
responses are separate checks. [HTTP/3](https://www.rfc-editor.org/rfc/rfc9114.html)
instead runs over QUIC on UDP and does not use this TCP sequence. A successful
TCP connect cannot prove application health.

Binding chooses a socket's local address. `127.0.0.1` means IPv4 loopback;
`0.0.0.0` means all local IPv4 addresses, not “localhost” and not a firewall
exception. [ip.7](https://man7.org/linux/man-pages/man7/ip.7.html) IPv6 has its own addresses and routes: `::1` is loopback and `::`
is the wildcard. Whether an IPv6 listener also accepts IPv4 depends on socket
options and system configuration. Never infer dual-stack reachability from a
port number alone. [ipv6.7](https://man7.org/linux/man-pages/man7/ipv6.7.html)

## Three practical interpretations

The following inspection commands need iproute2 and, for `getent`, NSS tools.
They do not change routes, addresses or listeners. Missing tools in a minimal
image are not evidence of a broken network.

### 1. An address is not a usable route

```bash
ip address show dev lo
ip route get 127.0.0.1
ip -6 route get ::1
```

The address listing shows what is assigned to loopback. `route get` asks the
kernel to resolve a route; it does not send a probe. Check the chosen device
and source address. An IPv6 lookup can fail if IPv6 is disabled. Even a sensible
route says nothing about whether a peer application is listening. [ip-route.8](https://man7.org/linux/man-pages/man8/ip-route.8.html)

### 2. A resolved name is not a connection

```bash
getent ahosts localhost
ss -lnt
```

`getent` follows the configured host lookup path rather than testing DNS alone.
`ss` uses `-l` for listening sockets, `-n` for numeric addresses/ports and `-t`
for TCP. Compare the listener's address family and bind address with the client's
actual destination. A loopback listener does not accept traffic addressed to a
host's external IPv4 address. [ss.8](https://man7.org/linux/man-pages/man8/ss.8.html)

### 3. Observe both ends of your own connection

This short Python 3 lab binds only IPv4 loopback, chooses an available port and
closes all sockets on exit. Timeouts prevent indefinite blocking. It serves no
files and requires no background server. [socket](https://docs.python.org/3/library/socket.html)

```bash
python3 - <<'PY'
import socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
    listener.settimeout(2)
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    with socket.create_connection(listener.getsockname(), timeout=2) as client:
        connection, peer = listener.accept()
        with connection:
            connection.settimeout(2)
            print('client:', client.getsockname(), '->', client.getpeername())
            print('server:', connection.getsockname(), '<-', peer)
            client.sendall(b'x')
            assert connection.recv(1) == b'x'
PY
```

The client's local port differs from the listening port. The accepted server
socket has reversed endpoints. This demonstrates TCP transport, not HTTP or TLS.

## Host and container are different viewpoints

Network namespaces separate interfaces, routes and socket tables. [namespaces.7](https://man7.org/linux/man-pages/man7/namespaces.7.html) A
container's `127.0.0.1` normally refers to its own namespace, not its host.
Container runtimes may connect namespaces through virtual interfaces, routing,
NAT or port forwarding; host-network mode changes those assumptions. Inspect
from the affected viewpoint before changing bind addresses or publishing ports.

For symptom-by-symptom diagnosis, continue with the existing
[network connectivity troubleshooting guide](../troubleshooting/network-connectivity.md).
The iproute2 commands above were documentation-checked but not executed in this
validation environment because `ip` and `ss` were unavailable; the loopback lab
and `getent` example were executed.

## Check your understanding

- Why can name resolution succeed while TLS fails?
- How can several connections share the same server port?
- Why might host loopback work while container loopback fails?
