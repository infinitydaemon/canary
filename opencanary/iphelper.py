import struct
import socket

def ip2int(addr: str) -> int:
    """
    Convert an IP address from string format to integer format.
    """
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def check_ip(ip: str, network_range: str) -> bool:
    """
    Test if an IP address is in a given network range.
    
    The network range is expected to be in CIDR notation format. If no subnet
    mask is given, /32 is used. Returns True if the IP is in the range, False
    otherwise.
    """
    network_addr, subnet_mask = network_range.split('/')
    subnet_mask = int(subnet_mask) if subnet_mask else 32
    try:
        network_addr_int = ip2int(network_addr)
        ip_int = ip2int(ip)
        subnet_mask_int = (0xFFFFFFFF << (32 - subnet_mask)) & 0xFFFFFFFF
        return (ip_int & subnet_mask_int) == (network_addr_int & subnet_mask_int)
    except (socket.error, struct.error):
        return False
