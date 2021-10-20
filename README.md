# Border Gateway Protocol

A means of routing packets between autonomous systems.

Care is taken to optimize:

- The most efficient path possible
- The least amount of storage required in each network hop
- Dynamic grouping abilities of routes

## Implementation

### Objects

#### Ip Address

A single, unique host within a network space.
An IP (*Internet Protocol*) address is a four-byte identifier, allowing binary messages to be delivered across a series of routers, or distinct, autonomous systems.

An `IpAddr` may be constructed from a:

- 32-bit integer
- Array of 4-bytes
- Dotted-decimal string

And may also be converted from an object into any of these forms.

Finally, convenience methods such as comparing addresses for equality or bit-shifting is exposed in the class API.

In order to allow dynamic creation of constant, *special* addresses at runtime, some accessor methods are provided in the address API.
Getters for the loopback, broadcast, and other addresses are available.

#### Ip Mask

Applied to an IP address, the mask essentially discards a portion of the bits.
This allows for addresses that occupy the same network, but represent different hosts, to be stored as a single address space, within which all addresses that the mask is applied to will yield the same representative, base address.
As such, the IP mask for a network will get progressively more precise as the network is traversed, and the destination target becomes closer to the packet.

For example, a home-network will likely only have one outgoing connection to an ISP (Internet Service Provider).
Thus, in order for any device on the network to communicate with an external entity, a packet must be sent along this single connection.
Conversly, though, the packet may need to take a multitude of different possible routes to reach its destination.
In order to ensure that each network hop does not have to store the routing information of the entire IP network space, masks are used.
Once a packet has left the home network, the ISP may determine where to forward a packet based on which connections are available to the physical router.
Along which interface the router decides to forward the packet will be determined based on which mask provides the most specific advancement in the transitting packet's mask resolution process.
This will yield the most efficient route for the packet to reach its destination, and thus the least amount of work required for the network to process any client's communications.

An IP mask object is composed of a network-identifying prefix, and a host-identifying suffix.
The mask may be represented as an IP address; the IP address that when bit-and'ed to another address will yield the network represented by a host.
All hosts in the same network will have the same address, when the mask is applied to them.

Similarly to the IP address API, the IP mask API offers a means of comparing, bit-shifting, and converting into an integer.
If other methods are necessary, any mask object may first be converted into an address object, and manipulated further from there.

#### Ip Network

A combination of an IP mask and some base IP address.
Inclusion in a network may be determined by:

1. Taking a host's IP address
1. Bit-And'ing this address with the network's IP mask
1. Comparing this address for exact equality to the network's base IP address

As the network is an aggregation of individual hosts, the numerical minimum and maximum addresses may be retrieved.
Also, the size and inclusion in the network may be determined via the API, and conversion into an iterator of addresses is supported.

Considering the network space as a tree, with each branch yielding a more-specific network mask and a smaller subset of child networks, the direct supernet or two child subnets may be accessed.
Tests for whether a network is one of these two is also provided.

Finally, more convenience methods are offered such as equality, string representation, and manipulating the size of the network.

#### Network Class

A network class is a form of IP network, predating the method of utilizing a mask and base-address.

By exmanining the first octet of an IP address, the associated class may be determined.
These are statically-determined and fixed-size.
As such, there are not many options for choosing a network size, with a very limited number of networks occupying a huge group of address spaces.

Each class is associated with an IP mask, but may not be stepped at a bit-level, and instead must transition between byte-level indications of a network prefix and host suffix.
