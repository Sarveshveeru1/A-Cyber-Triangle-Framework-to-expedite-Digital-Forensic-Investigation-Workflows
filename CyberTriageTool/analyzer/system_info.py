# analyzer/system_info.py

import platform
import socket
import getpass
import psutil
import datetime
import json

def collect_system_info():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    info = {
        "hostname": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "username": getpass.getuser(),
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_cores": psutil.cpu_count(logical=True),
        "memory": {
            "total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "used_gb": round(psutil.virtual_memory().used / (1024 ** 3), 2),
            "free_gb": round(psutil.virtual_memory().available / (1024 ** 3), 2)
        },
        "disk_usage": {
            part.mountpoint: {
                "total_gb": round(psutil.disk_usage(part.mountpoint).total / (1024 ** 3), 2),
                "used_gb": round(psutil.disk_usage(part.mountpoint).used / (1024 ** 3), 2),
                "free_gb": round(psutil.disk_usage(part.mountpoint).free / (1024 ** 3), 2)
            }
            for part in psutil.disk_partitions() if 'cdrom' not in part.opts
        }
    }
    return info

def save_system_info_to_file(filepath='output/system_info.json'):
    info = collect_system_info()
    with open(filepath, 'w') as f:
        json.dump(info, f, indent=4)
    print(f"✅ System information saved to {filepath}")
