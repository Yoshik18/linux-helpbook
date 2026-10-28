# 9. Networking from the command line

[Contents](../README.md) | [Previous: storage](08-storage.md) | [Next: services](10-services.md)

A page will not open. That could mean your computer cannot find the server's address, cannot reach that address, cannot open the requested connection, or has received an error from the application itself. Those are different problems. Restarting networking before finding out which one happened can interrupt working connections without fixing the failed one.

This chapter follows one small web request from a name to a response. First we will use a server on the same computer, so the result does not depend on an internet connection. Then we will use the same reasoning to read interface and route information and investigate an authorized remote service. The inspection commands do not change network settings.

## On this page

- [What a web request needs](#what-a-web-request-needs)
- [Make a small local service](#make-a-small-local-service)
- [Ask for the page by address](#ask-for-the-page-by-address)
- [Read the response, including errors](#read-the-response-including-errors)
- [Put a name in front of the address](#put-a-name-in-front-of-the-address)
- [Check where the server is listening](#check-where-the-server-is-listening)
- [Stop the server and interpret the failure](#stop-the-server-and-interpret-the-failure)
- [Inspect the way out of your computer](#inspect-the-way-out-of-your-computer)
- [Apply the same questions to HTTPS](#apply-the-same-questions-to-https)
- [What ping can and cannot tell you](#what-ping-can-and-cannot-tell-you)
- [Keep a useful diagnosis](#keep-a-useful-diagnosis)
- [Further reading](#further-reading)

## What a web request needs

We will ask one program on this computer to send a small file to another program on the same computer. The program waiting to answer is the **server**; the one asking is the **client**. We can observe a successful request before involving another machine, a name lookup service, or an internet connection.

For the first request, you only need two destination details: an address that means this computer, and a port number that selects our waiting program. The next commands make both visible. We will explain the other parts of a remote web request when they become relevant.

## Make a small local service

You need Python 3 and `curl` for this example. Python includes a basic file-serving program; `curl` is a command-line client for requesting URLs. If either command is missing, that is a missing tool, not evidence that networking is broken. Follow your distribution's installation instructions only if you are allowed to install software.

Use a new, empty practice directory that contains no private files. Run these commands inside it:

```bash
mkdir web
printf 'network check passed\n' > web/index.html
```

`mkdir web` creates a child directory. `printf` writes the quoted text, with `\n` producing a newline. The shell's `>` puts that output into `web/index.html` instead of on the screen. It would replace an existing file, which is why this example starts in a fresh directory. A file named `index.html` is the page this server will return for `/`, the top-level web path.

The address `127.0.0.1` sends a request back to this same computer. It is an IPv4 **loopback** address. In a container, that means the container's own networking environment, not necessarily its host. The port `8765` is a software number that distinguishes our server from other programs accepting connections. It is not a physical connector.

A server waiting for new connections is **listening**. The `--bind` option below keeps this server on the loopback address, so this example does not deliberately expose it to other machines.

Start the server in this terminal:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory web
```

`python3` runs Python. `-m http.server` runs its included HTTP server module. `8765` selects the port. `--bind 127.0.0.1` tells it to accept connections only at the IPv4 loopback address. `--directory web` limits the files it serves to our practice directory. Leave the command running and open a second terminal for the client commands. The second terminal can be in any directory.

The server occupies the first terminal because it is waiting for requests. It will print startup information and request logs there. That is expected; a server does not need to return immediately to the shell to be working.

If it reports `Address already in use`, it could not claim the requested address and port. Do not stop an unfamiliar process to make room. Choose another unused high port, such as 8766, and use that same number in every later server and client command. If the server did not start, the following request cannot test it.

This server is for local practice, not for publishing a website. Keep the explicit loopback binding. Also keep the served directory free of secrets and symbolic links to other files: Python's simple server can follow those links.

## Ask for the page by address

In the second terminal, run:

```bash
curl --noproxy '*' --max-time 5 http://127.0.0.1:8765/
```

The URL says exactly what we want:

- `http://` selects ordinary HTTP, without TLS.
- `127.0.0.1` selects this local networking environment.
- `:8765` selects the listening port rather than HTTP's default port 80.
- The final `/` selects the top-level path.

`--max-time 5` limits the entire operation to five seconds. Without a time limit, some failures can leave you waiting much longer. `--noproxy '*'` tells curl not to use a proxy for this request. The quoted `*` means all destinations to curl; quotes keep the shell from turning the asterisk into filenames. This is appropriate for our direct loopback example, not a reason to bypass an organization's required proxy for external traffic.

The observed response body from the local example was:

```text
network check passed
```

Curl can also print a progress meter on its error-output stream. That meter is not part of the page. The server terminal should record the request separately.

Why is this stronger evidence than merely seeing an address on an interface? The client connected to a specific address and port, sent an HTTP request, and received the file content. It demonstrates that this particular local request worked. It says nothing yet about internet access, another port, HTTPS, or another machine reaching this server.

## Read the response, including errors

The client and server need rules for their conversation. **HTTP**, the Hypertext Transfer Protocol, defines web requests and responses. A response contains a status, descriptive lines called **headers**, and, when appropriate, the content or **body**. The earlier curl result was the body. Now we will inspect the status and headers separately.

To look at the descriptive part of the response rather than download the page body, ask curl to make a **HEAD request**. HEAD asks the server for response headers without a response body:

```bash
curl --noproxy '*' -I --max-time 5 http://127.0.0.1:8765/
```

The capital `-I` selects HEAD. It is not a lowercase `-i`, which includes headers alongside the body of an ordinary request.

Here is a schematic excerpt of the headers, omitting changing dates and version information:

```text
HTTP/1.0 200 OK
Content-type: text/html
Content-Length: 21
```

`HTTP/1.0` is the response's HTTP version. `200` is the HTTP status code; here it means the request succeeded. `Content-type` describes the kind of content, and `Content-Length` gives its size in bytes. HEAD itself does not return those 21 body bytes. The successful body request above is a more direct test of retrieving the content.

Now ask for a path that does not exist:

```bash
curl --noproxy '*' -I --max-time 5 http://127.0.0.1:8765/missing
```

The first response line observed in this example was:

```text
HTTP/1.0 404 File not found
```

This is not a broken network connection. The server understood enough of the request to report that `/missing` was unavailable. We deliberately changed the HTTP path while keeping the address and port the same. The correction is to request `/` again, not to change an interface or route.

The status code belongs to HTTP. It is separate from the shell's **exit status**, the number a command returns when it finishes. Curl normally treats receiving an HTTP response as a completed transfer even when that response says `404`. The tested 404 command above returned shell status 0. To make HTTP errors count as command failures, use `--fail`:

```bash
curl --noproxy '*' --fail -I --max-time 5 http://127.0.0.1:8765/missing
```

In the local check this returned shell status 22 and printed this error in addition to the headers and progress information:

```text
curl: (22) The requested URL returned error: 404
```

The meaning of the server response has not changed. We changed how curl reports it to the shell. That distinction matters when a script decides whether to continue after a command.

Other HTTP statuses also belong at the application level. `401` usually requests authentication, `403` indicates the request was forbidden, and a `500` indicates an internal server error. A `502` or `504` often comes from a server acting as an intermediary that could not obtain a usable response from another service. They are evidence of an HTTP response from somewhere in the request path, not proof that every backend service is healthy. Do not start changing passwords or network settings based only on the number; read the service's explanation and logs if you are authorized to do so.

Some applications reject HEAD even when a normal page request works. If `-I` produces a method-related error, compare with an ordinary curl request before deciding that the application is down.

## Put a name in front of the address

People usually type a name rather than a number. Translating a name into candidate addresses is **name lookup**, also called name resolution. DNS, the Domain Name System, provides a distributed directory for this purpose. Linux may also obtain names from a local file or another configured source. A successful lookup supplies addresses; it does not prove an application will answer there.

We have proved the numeric-address request works. Now ask Linux what address it associates with the name `localhost`:

```bash
getent ahosts localhost
```

On systems using the GNU C library, `getent` reads entries through the system's configured name-service mechanism. `ahosts` asks for address records usable by networking programs, and `localhost` is the name to look up. This is not a direct instruction to contact a DNS server. Linux commonly knows this particular name locally.

An observed excerpt from the local check was:

```text
127.0.0.1       STREAM localhost
127.0.0.1       DGRAM
127.0.0.1       RAW
```

The full check repeated these address rows. Repetition does not imply several different computers. `STREAM` describes a stream-style socket, the style used for our TCP connection. `DGRAM` describes message-oriented communication, such as UDP, the User Datagram Protocol. UDP sends individual messages without TCP's reliable ordered stream. `RAW` is a lower-level socket type that we do not need here. None of these rows reports an open port or proves a server is listening.

Your machine may also return `::1`, or a different ordering or number of rows. Name lookup can return several candidate addresses. The client decides which ones to try, and different clients can use different lookup behavior. A browser with its own DNS configuration need not behave exactly like `getent`.

Now request the same page by name:

```bash
curl --noproxy '*' --max-time 5 http://localhost:8765/
```

This also returned `network check passed` in the local check. The known-working numeric request gave us a useful comparison. If the numeric request works but the name-based one does not, investigate lookup and address selection before blaming the server's file content. For example, a client might select the IPv6 loopback address while this server listens only on IPv4. The mere presence of a name in a lookup result does not establish that all its addresses work.

For a remote name, the corresponding inspection would be:

```bash
getent ahosts example.com
```

This is a conditional example for an approved public name, not an externally executed test here. It may contact your configured lookup services. Use the actual service name you are authorized to diagnose. An empty result can indicate an unknown or misspelled name, an unavailable lookup service, or a configuration problem. It does not by itself identify which cause applies.

On GNU/Linux, lookup order is configured through `/etc/nsswitch.conf`; `/etc/hosts` can supply local name mappings. DNS-related configuration may be managed by a distribution service, a VPN, or a link at `/etc/resolv.conf`. A VPN is a connection that carries traffic through another network and can also change how names are found. Do not replace resolver files just because a tutorial uses different contents. First identify the mechanism your distribution and network actually use.

## Check where the server is listening

Our local HTTP request uses **TCP**, the Transmission Control Protocol. It provides an ordered stream of bytes between the client and server, handling missing or reordered data along the way. It does not decide whether a page is correct. The operating system represents a communication endpoint with an object called a **socket**. A listening TCP socket is waiting to accept new connections.

A successful request proves more than a listening entry, but a listening entry can explain a failed request. On Linux systems with the `ss` utility installed, inspect TCP listeners:

```bash
ss -lnt
```

`ss` displays socket information. `-l` selects listening sockets, `-n` keeps addresses and ports numeric, and `-t` selects TCP. These single-letter options are combined after one hyphen. This reads local state; it does not send a test request to each listener.

The following is a schematic, not output captured from the local test environment, where `ss` was unavailable:

```text
State   Recv-Q Send-Q Local Address:Port Peer Address:Port
LISTEN  0      5      127.0.0.1:8765      0.0.0.0:*
```

Focus first on `LISTEN` and `Local Address:Port`. They identify the address and port on which this socket accepts new connections. The queue columns concern pending connections and limits; a listener with an empty queue is not necessarily idle or broken. `Peer Address:Port` is not one established remote client here. For a listener, the wildcard means it is not restricted to one fixed peer.

The local binding determines where connections can arrive:

- `127.0.0.1:8765` accepts IPv4 loopback connections. Another machine cannot use your loopback address to reach it; its own `127.0.0.1` refers to itself.
- `0.0.0.0:8765` means all local IPv4 addresses. It does not mean “the internet has permission to connect.”
- `[::1]:8765` is IPv6 loopback. Square brackets separate the IPv6 address's colons from the port separator.
- `[::]:8765` means all local IPv6 addresses. Whether that socket also accepts IPv4 depends on socket and system settings. Do not assume it does.

A service listening on one specific non-loopback address is more restricted than a wildcard listener. A **firewall**, a set of traffic-allowing or traffic-blocking rules, may impose additional limits. Routing and upstream network devices may also prevent access. Thus an all-address listener is local evidence only. External reachability requires a test from an authorized client on the relevant network, using the intended address, port and protocol. This chapter does not perform that test or change firewall rules.

A socket can be listening while the application responds with errors or never produces useful content. That is why the earlier curl request matters. To inspect UDP sockets, `ss -lnu` replaces TCP's `-t` with UDP's `-u`; UDP does not have TCP's connection-listening behavior. Do not interpret its states as if they were TCP states.

## Stop the server and interpret the failure

In the first terminal, press Ctrl+C. That interrupts the foreground Python server. Make sure the terminal returns to a shell prompt. Then repeat the address-based request in the second terminal:

```bash
curl --noproxy '*' --max-time 5 http://127.0.0.1:8765/
```

After the tested server stopped, curl returned shell status 7. Its error line was:

```text
curl: (7) Failed to connect to 127.0.0.1 port 8765 after 0 ms: Could not connect to server
```

The address did not change, the page file still existed, and no name lookup was needed. What changed was that our server was no longer accepting connections. Here the correction is to restart the same Python command, not to edit the name-service configuration. Curl's exact wording and timing vary by version; some clients explicitly say `Connection refused`.

A refusal usually means that the connection attempt received an immediate rejection, often because no service is listening on the requested address and port. A firewall can also reject traffic actively. It does not prove the intended application was reached, and “the machine is off” is not the only explanation.

A **timeout** means the permitted time expired without completing the operation. Packets may have been silently dropped, a reply path may be broken, or a server may have accepted the connection but stalled later. Curl commonly returns status 28 for its time limits. Read which phase its message describes. A whole-transfer limit such as `--max-time` is not exclusively a connection timeout. We did not manufacture a timeout by altering live network rules.

The contrast is important: a refusal is a negative response at connection setup; a timeout is the absence of timely completion; a `404` is an HTTP response after the conversation got further. They suggest different next questions.

When finished, with the server stopped, remove only the files made for this example. In the original practice directory:

```bash
rm web/index.html
rmdir web
```

`rm` removes our page. `rmdir` removes the directory only if it is empty. If it refuses because there are other files, inspect them rather than adding a recursive deletion option.

## Inspect the way out of your computer

Linux represents a wired, Wi-Fi, or software-created connection point as a **network interface**. An interface name identifies that connection point, while an **IP address** identifies a network destination or source. IP means Internet Protocol; it carries data in pieces called packets. Dotted addresses such as `127.0.0.1` use IPv4. Colon-separated addresses such as `::1`, the IPv6 loopback address, use IPv6. These are different address families; success with one does not prove the other works.

For a destination elsewhere, Linux chooses where to send packets next. That choice follows a **route**. It can lead directly through an interface or toward another machine that forwards packets, called a **gateway**. The route describes a planned next step, not proof that the destination will answer.

The local example did not need a cable, Wi-Fi, or an internet gateway. For a remote service, inspect the connection points and Linux's route choice as well. These commands require `ip`, usually supplied by the iproute2 package. They are read-only forms. Do not add addresses, replace routes, or bring interfaces down while trying to understand an outage.

Start with:

```bash
ip address show
```

`ip` is the network-inspection and configuration tool; `address` selects interface addresses, and `show` requests current information. A schematic excerpt, using documentation-only addresses rather than a machine's real details, is:

```text
2: enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 state UP
    inet 192.0.2.10/24 scope global enp1s0
```

`enp1s0` is the interface name. `UP` means it is enabled administratively; `LOWER_UP` indicates that the underlying link reports being up. Neither proves a remote service works. `inet` introduces an IPv4 address. `/24` describes the network prefix: the first 24 address bits identify the network portion. An `inet6` line would introduce an IPv6 address. The remaining flags and the maximum packet size, shown as `mtu`, are useful for deeper investigation but are not a first verdict about the page request.

Do not read `scope global` as “publicly reachable.” Linux also uses that label for addresses that are not public internet addresses. Look for the address family and interface relevant to your request. Machines with virtual connections, containers or VPNs can show many interfaces; not every down interface is a problem.

Next read the IPv4 routes:

```bash
ip route show
```

A schematic example is:

```text
default via 192.0.2.1 dev enp1s0
192.0.2.0/24 dev enp1s0 scope link src 192.0.2.10
```

The second line says that the listed local network is reached through `enp1s0`. `src` identifies a preferred source address for traffic using that route. The first line is the **default route**, used when no more specific applicable route matches. `via` identifies a gateway; `dev` identifies the interface. The destination website is not usually the gateway itself. The gateway is the next machine asked to carry the packet onward.

Route selection favors a more specific matching prefix within the selected routing table. Systems with VPNs or extra routing policies can choose among several tables, so the short listing is not the whole story. To ask what route Linux would choose for one IPv4 destination, use:

```bash
ip route get 198.51.100.20
```

`get` requests a route decision for that address. It does not send a probe to the destination. `198.51.100.20` is a documentation-only example; substitute an address actually returned for your approved service when diagnosing it. Read the selected interface, gateway if any, and source address. A plausible selection still does not prove packets or replies can travel successfully.

IPv6 routes are separate:

```bash
ip -6 route show
```

`-6` selects IPv6. An IPv4 default route cannot stand in for a missing IPv6 route. Conversely, no IPv4 default route is not proof of a fault on a machine designed to use IPv6 only. Match your observations to the address family the client is attempting.

These interface and route examples were not executed in the chapter's local check because `ip` was unavailable. Their displayed output is explicitly schematic. There is no need to install or reconfigure networking merely to reproduce their layout.

## Apply the same questions to HTTPS

Ordinary HTTP does not protect the conversation from someone who can observe or alter its network path. **TLS**, Transport Layer Security, negotiates encryption and normally checks the server's identity using a certificate. A certificate links an identity, such as a website name, to cryptographic information checked against trusted issuers. **HTTPS** is HTTP protected by TLS.

A configured intermediary, called a **proxy**, may make part of the connection for your client. The direct loopback example deliberately avoided one. For the usual TCP-based remote HTTPS request, the pieces now fit together as:

```text
name -> candidate IP address -> route -> TCP connection to a port
     -> TLS identity and encryption checks -> HTTP response
```

This is a reasoning aid, not every possible web arrangement. For example, HTTP/3 uses a different transport rather than TCP.

For a service you are allowed to contact, an application request tests more of the path than inspecting configuration does. This conditional example contacts a public endpoint and was not run as part of the local checks:

```bash
curl -I --max-time 5 https://example.com/
```

Here `https://` asks for TLS-protected HTTP and, with no explicit port, normally uses port 443. `-I` and `--max-time 5` have the same meanings as before. Unlike our loopback example, this command leaves proxy use at the system's configured default. If your network requires a proxy, it may be part of the path being tested.

Interpret the result in the order the request needed things to work:

1. **Could the name be found?** A message such as `Could not resolve host` means curl could not obtain an address for the name at that point. Check the spelling and compare with the system lookup result. If the message names a proxy instead, the failure may concern the proxy's name, not the website's.
2. **Could a connection be made?** A refusal or connection-stage timeout precedes any HTTP response from the destination. Check the requested port, chosen address family and route. If you own the server, compare its listener with the intended address and port. Do not turn off a firewall merely to see whether something changes.
3. **Did TLS checks succeed?** An untrusted issuer, an expired certificate, or a certificate for a different name is a security or configuration issue, not an HTTP `404`. A wrong local clock can also make a certificate appear outside its valid dates. Other TLS failures can concern protocol compatibility or an intermediary rather than a certificate. Follow the actual message.
4. **What did HTTP report?** A returned status such as `200`, `403` or `500` means an HTTP-speaking endpoint answered. If there are intermediaries, it may not be the final application. Continue with the response and application logs rather than returning immediately to basic address configuration.

Do not “fix” a TLS error by routinely adding `-k`, the curl option that disables certificate verification. Encryption without the intended identity check does not answer whether you reached the right service. Likewise, replacing a hostname with a numeric address in an HTTPS URL changes the identity being checked and can change which site the server selects. The simple address-versus-name comparison from our plain HTTP fixture does not transfer unchanged to a name-based HTTPS service.

A response is still limited evidence. It establishes the result of one request at one time. A successful HEAD request does not establish that logging in works, that a large download completes, or that another client can reach the same endpoint. Keep the exact URL, method, time limit and error message with your diagnosis.

## What ping can and cannot tell you

Linux can send a small “please reply” message to an address without asking for a web page. The common tool is `ping`. It uses ICMP, the Internet Control Message Protocol, rather than opening a TCP connection to the website's port.

A bounded local example is:

```bash
ping -c 2 -W 1 127.0.0.1
```

For the common Linux iputils version, `-c 2` sends two echo requests and `-W 1` sets the reply-wait setting to one second. Timing details and options can differ in other implementations. Without a count, ping commonly continues until interrupted. Some environments restrict permission to send these messages.

The local check's summary included this observed line:

```text
2 packets transmitted, 2 received, 0% packet loss, time 1026ms
```

That means both of those echo requests received replies in that check. It does not show that port 8765 is open. Loopback can reply to ping with the Python server stopped because the echo replies are handled independently of the web server.

On a remote network, firewalls may allow web traffic but block or limit echo replies. No ping reply is therefore not proof that all connectivity is down. A reply does not verify DNS when you supplied a numeric address, does not verify TLS, and does not verify HTTP. Use it for the question it actually asks, not as a universal internet test. Contact remote addresses only when permitted; no remote ping is needed for this chapter's example.

## Keep a useful diagnosis

The aim is to narrow a failure without disturbing working parts. Our local example gave three distinct results for one address and port: a successful body request while the server was running, an HTTP `404` for a nonexistent path, and a failed connection after the server stopped. The right correction depended on which result we had, not on a general feeling that “the network is broken.”

For a real incident, record the intended name, address family, port, HTTP or HTTPS scheme, and path. Record whether the client used a proxy and whether the test ran on the server, on your laptop, or inside a container. These details identify the endpoint and the viewpoint. “It works locally” is not the same claim as “a user on another network can reach it.”

Then keep each observation with its limit. An address is local configuration. A route is a planned next hop. A name lookup provides candidate addresses. A listener is local readiness to accept connections. An HTTP response is an actual application-level conversation. Those observations complement one another; none should be stretched into a claim it cannot support.

Before sharing output, remove real addresses, internal names, account details, cookies, authorization headers and private URLs. Keep consistent placeholders so that someone reading the report can still tell which address was a gateway and which was a destination. The documentation addresses in this chapter are examples, not reachable targets or captured host configuration.

## Further reading

- [iproute2 documentation](https://www.kernel.org/pub/linux/utils/net/iproute2/)
- [Linux man-pages: ip(7)](https://man7.org/linux/man-pages/man7/ip.7.html)
- [curl manual](https://curl.se/docs/manpage.html)
- [Linux man-pages: socket(7)](https://man7.org/linux/man-pages/man7/socket.7.html)
- [ip-route(8): inspecting route selection](https://man7.org/linux/man-pages/man8/ip-route.8.html)
- [ss(8): inspecting sockets](https://man7.org/linux/man-pages/man8/ss.8.html)
- [getent(1): configured name-service lookups](https://man7.org/linux/man-pages/man1/getent.1.html)
- [Python: the simple HTTP server and its limits](https://docs.python.org/3/library/http.server.html)
