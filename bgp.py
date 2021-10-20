#!/usr/bin/env python3
"""A Border-Gateway Protocol Router Implementation."""
from __future__ import annotations

from enum import Enum, auto
from typing import Iterator, Optional, Tuple, Union


class IpAddr:
    """Encapsulates a single IP Address, representing a single host on a network."""

    # 255.255.255.255
    MAX_NUM = 0xFF_FF_FF_FF
    MIN_NUM = 0

    __slots__ = ["num"]

    def __init__(self, num: int):
        if not IpAddr.MIN_NUM <= num <= IpAddr.MAX_NUM:
            raise ValueError("Can only store a value with 4-bytes!")
        self.num = num

    @classmethod
    def from_octets(cls, octets: list[int]) -> IpAddr:
        """Creates an Ip Address object from a collection of four-octets."""
        val = int.from_bytes(octets, "big", signed=False)
        return cls(val)

    @classmethod
    def from_str(cls, text: str) -> IpAddr:
        """Creates an Ip Address object from the provided dotted-decimal string representation."""
        byte_buf = [int(x) for x in text.split(".")]
        return cls.from_octets(byte_buf)

    def __int__(self) -> int:
        """The numerical, integer representation of this address object."""
        return self.num

    def octets(self) -> bytes:
        """Gets an array of four-bytes, representing the octets of this ip address."""
        return int(self).to_bytes(4, "big", signed=False)

    def __str__(self) -> str:
        return ".".join(str(octet) for octet in self.octets())

    def __eq__(self, other) -> bool:
        if isinstance(other, IpAddr):
            return int(self) == int(other)
        if isinstance(other, int):
            return int(self) == other
        return False

    def __lt__(self, other: IpAddr) -> bool:
        return int(self) < int(other)

    def __gt__(self, other: IpAddr) -> bool:
        return int(self) > int(other)

    def __and__(self, other: Union[IpAddr, int]) -> IpAddr:
        if isinstance(other, IpAddr):
            return IpAddr(int(self) & int(other))
        return IpAddr(int(self) & other)

    def __lshift__(self, amt: int) -> IpAddr:
        new_num = int(self) << amt
        return IpAddr(new_num % IpAddr.MAX_NUM)

    def __rshift__(self, amt: int) -> IpAddr:
        new_num = int(self) >> amt
        return IpAddr(new_num)

    def __invert__(self) -> IpAddr:
        return IpAddr(~int(self))

    def __bytes__(self) -> bytes:
        return self.octets()

    @classmethod
    def get_local_addr(cls) -> IpAddr:
        """Getter for the address used to communicate with the local network."""
        return cls(0)

    @classmethod
    def get_loopback_addr(cls) -> IpAddr:
        """Getter for the loopback address."""
        return cls.from_octets([127, 0, 0, 0])

    @classmethod
    def get_broadcast_addr(cls) -> IpAddr:
        """Getter for the broadcast address (of the router) on the local network."""
        return cls.from_octets([255, 255, 255, 255])


class IpMask:
    """Encapsulates a mask, which may be applied to an address in order to determine
    inclusion in a network."""

    MAX_NUM = 32
    MIN_NUM = 0

    __slots__ = ["_num_network_bits"]

    def __init__(self, num_network_bits: int):
        self.num_network_bits = num_network_bits

    @property
    def num_network_bits(self) -> int:
        """The number of **prefix** network bits in any address applied to this mask."""
        return self._num_network_bits

    @num_network_bits.setter
    def num_network_bits(self, val: int):
        if not IpMask.MIN_NUM <= val <= IpMask.MAX_NUM:
            raise ValueError("Can only create a mask composed of 32-bits!")
        self._num_network_bits = val

    @property
    def num_host_bits(self) -> int:
        """The number of **suffix** host-identifier bits in any address applied to this mask."""
        return IpMask.MAX_NUM - self.num_network_bits

    def as_addr(self) -> IpAddr:
        """Converts this mask into an Ip Address object,
        which may be bit-and'ed to some host address."""
        num = (IpAddr.MAX_NUM << self.num_host_bits) % IpAddr.MAX_NUM
        return IpAddr(num)

    def apply(self, addr: IpAddr) -> IpAddr:
        """Applies this address-mask to the base address.
        Used in conjunction with some base-address, a network may be sub-divided."""
        mask = self.as_addr()
        masked_addr = int(mask) & int(addr)
        return IpAddr(masked_addr)

    def __eq__(self, other: IpMask) -> bool:
        return self.num_network_bits == other.num_network_bits

    def __int__(self) -> int:
        return self.num_network_bits

    def __lshift__(self, amt: int) -> IpMask:
        new_num = self.num_network_bits - amt
        return IpMask(new_num)

    def __rshift__(self, amt: int) -> IpMask:
        return self << -amt


class IpNet:
    """An Ip Network; a collection of hosts identified by Ip Addresses."""

    __slots__ = ["_base", "_mask"]

    def __init__(self, base: IpAddr, mask: IpMask):
        self._base = base
        self._mask = mask

    @property
    def mask(self) -> IpMask:
        """The Ip Mask associated with this network."""
        return self._mask

    @property
    def addr(self) -> IpAddr:
        """The base Ip Address associated with this network."""
        return self.mask.apply(self._base)

    def min_addr(self) -> IpAddr:
        """Getter for the minimum (numerically) ip address within this network space."""
        return self.addr

    def max_addr(self) -> IpAddr:
        """Getter for the maximum (numerically) ip address within this network space."""
        return IpAddr(int(self.min_addr()) + self.num_hosts() - 1)

    def num_hosts(self) -> int:
        """Getter for the number of unique addresses within this network."""
        return pow(2, self.mask.num_host_bits)

    def contains(self, addr: IpAddr) -> bool:
        """Determines whether the host identified by the provided address
        is contained within this network."""
        return self.addr == self.mask.apply(addr)

    def is_adjacent(self, other: IpNet) -> bool:
        """Tests whether the supplied network is adjacent, but NOT the same as this network."""
        # Same network => Can't be adjacent
        if self == other:
            return False
        # Different mask => Can't be adjacent
        if self.mask != other.mask:
            return False
        # One less network bit, to consume the adjacent networks
        new_mask = IpMask(self.mask.num_network_bits - 1)
        return new_mask.apply(self.addr) == new_mask.apply(other.addr)

    def get_subnets(self) -> Tuple[IpNet, IpNet]:
        """Getter for the two subnets directly descended from this network."""
        new_mask = IpMask(self.mask.num_network_bits + 1)
        return (IpNet(IpAddr(0), new_mask), IpNet(IpAddr(0), new_mask))

    def get_supernet(self) -> IpNet:
        """Getter for the supernet which is a direct parent of this network."""
        new_mask = IpMask(self.mask.num_network_bits - 1)
        return IpNet(self.addr, new_mask)

    def is_supernet(self, other: IpNet) -> bool:
        """Tests whether the supplied network is a supernet of this network,
        and contains this network."""
        # Must have a less-significant number of network bits, to encapsulate more host addresses
        if self.mask.num_network_bits >= other.mask.num_network_bits:
            return False
        return self.contains(other.addr)

    def is_subnet(self, other: IpNet) -> bool:
        """Tests whether the supplied network is a subnet of this network,
        and is contained within this network."""
        return other.is_supernet(self)

    def __eq__(self, other: IpNet) -> bool:
        return self.addr == other.addr and self.mask == other.mask

    def __str__(self) -> str:
        return f"{str(self.addr)}/{self.mask.num_network_bits}"

    def __len__(self) -> int:
        """The number of hosts in this network."""
        return self.num_hosts()

    def __iter__(self) -> Iterator[IpAddr]:
        curr = int(self.min_addr())
        while curr <= self.max_addr():
            yield IpAddr(curr)
            curr += 1

    def __lshift__(self, amt: int) -> IpNet:
        return IpNet(self.addr, self.mask << amt)

    def __rshift__(self, amt: int) -> IpNet:
        return IpNet(self.addr, self.mask >> amt)


class NetClass(Enum):
    """An obselete format of Ip-class versioning, predating CIDR subnetting.

    Inclusion in each class is determined by the first octet:
    A  |    0-127  |  0000_0000 - 0111_1111  |  0***_****  |
    B  |  128-191  |  1000_0000 - 1011_1111  |  10**_****  |
    C  |  192-223  |  1100_0000 - 1101_1111  |  110*_****  |
    D  |  224-239  |  1110_0000 - 1110_1111  |  1110_****  |
    E  |  240-255  |  1111_0000 - 1111_1111  |  1111_****  |
    """

    A = auto()
    B = auto()
    C = auto()
    D = auto()
    E = auto()

    def get_mask(self) -> Optional[IpMask]:
        """Getter for the subnet mask associated with this address class.
        NOTE: for classes D and E, there is no associated mask, and `None` will be returned."""
        if self == NetClass.A:
            return IpMask(8)
        if self == NetClass.B:
            return IpMask(16)
        if self == NetClass.C:
            return IpMask(24)
        return None

    @staticmethod
    def from_addr(addr: IpAddr) -> NetClass:
        """Getter for the network class, determined by the first octet of the address."""
        octet, _, _, _ = addr.octets()
        if 0 <= octet <= 127:
            return NetClass.A
        if 128 <= octet <= 191:
            return NetClass.B
        if 192 <= octet <= 223:
            return NetClass.C
        if 224 <= octet <= 239:
            return NetClass.D
        return NetClass.E

    def __str__(self) -> str:
        if self == NetClass.A:
            return "A"
        if self == NetClass.B:
            return "B"
        if self == NetClass.C:
            return "C"
        if self == NetClass.D:
            return "D"
        return "E"
