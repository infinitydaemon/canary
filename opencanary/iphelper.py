import ipaddress

def ip2int(addr: str) -> int:
    """
    Convert an IP address from string format to integer format.
    
    Args:
        addr (str): The IP address in string format.

    Returns:
        int: The IP address in integer format.
    """
    return int(ipaddress.ip_address(addr))

def check_ip(ip: str, network_range: str) -> bool:
    """
    Test if an IP address is in a given network range.

    The network range is expected to be in CIDR notation format.
    Returns True if the IP is in the range, False otherwise.

    Args:
        ip (str): The IP address to check.
        network_range (str): The network range in CIDR notation.

    Returns:
        bool: True if the IP is in the range, False otherwise.
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        network = ipaddress.ip_network(network_range, strict=False)
        return ip_obj in network
    except ValueError:
        return False

# Example usage:
ip_to_check = "192.168.1.5"
network_range_to_check = "192.168.1.0/24"

if check_ip(ip_to_check, network_range_to_check):
    print(f"{ip_to_check} is in the network range {network_range_to_check}.")
else:
    print(f"{ip_to_check} is NOT in the network range {network_range_to_check}.")
