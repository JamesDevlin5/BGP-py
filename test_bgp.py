#!/usr/bin/env python3

from bgp import *

zero_ip = IpAddr(IpAddr.MIN_NUM)
zero_ip_str = "0.0.0.0"
ones_ip = IpAddr(IpAddr.MAX_NUM)
ones_ip_str = "255.255.255.255"


def test_addr_octets():
    assert bytes([0, 0, 0, 0]) == zero_ip.octets()
    assert bytes([255, 255, 255, 255]) == ones_ip.octets()


def test_addr_num():
    assert int(zero_ip) == 0
    assert int(ones_ip) == pow(2, 32) - 1


def test_addr_str():
    assert str(zero_ip) == zero_ip_str
    assert str(ones_ip) == ones_ip_str


def test_addr_from_str():
    assert zero_ip == IpAddr.from_str(zero_ip_str)
    assert ones_ip == IpAddr.from_str(ones_ip_str)
