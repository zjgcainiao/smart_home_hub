import psutil

def get_network_info():
    network_info = {
        "network_stats": psutil.net_if_stats(),
        "network_io_counters": psutil.net_io_counters(pernic=True),
        "network_addresses": psutil.net_if_addrs(),
    }
    return network_info