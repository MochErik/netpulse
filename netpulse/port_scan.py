"""High-speed TCP port scanner with banner grabbing."""

import socket
import concurrent.futures
from typing import List, Dict, Any, Union

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    1883: "MQTT",
    3000: "Node / Grafana",
    3306: "MySQL / MariaDB",
    5432: "PostgreSQL",
    6379: "Redis",
    8000: "HTTP Dev / FastAPI",
    8080: "HTTP Alt / CasaOS",
    8883: "MQTTS Secure",
    9000: "Portainer",
    9090: "Prometheus"
}


def probe_port(target: str, port: int, timeout_sec: float = 0.8) -> Dict[str, Any]:
    """Check if a TCP port is open and attempt service banner grabbing."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout_sec)
    
    banner = ""
    is_open = False
    try:
        sock.connect((target, port))
        is_open = True
        
        # Try grab banner
        try:
            sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n" if port in [80, 443, 8080, 3000] else b"\r\n")
            sock.settimeout(0.5)
            data = sock.recv(256)
            banner = data.decode(errors="ignore").strip().splitlines()[0] if data else ""
        except Exception:
            pass
    except Exception:
        is_open = False
    finally:
        sock.close()

    service_name = COMMON_PORTS.get(port, "Unknown")
    return {
        "port": port,
        "is_open": is_open,
        "service": service_name,
        "banner": banner[:60] if banner else None
    }


def scan_target_ports(target: str, ports: Union[List[int], range] = None, max_threads: int = 50) -> List[Dict[str, Any]]:
    """Scan a target across multiple TCP ports concurrently."""
    if ports is None:
        ports = sorted(list(COMMON_PORTS.keys()))
    
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_map = {executor.submit(probe_port, target, p): p for p in ports}
        for future in concurrent.futures.as_completed(future_map):
            res = future.result()
            if res["is_open"]:
                open_ports.append(res)
                
    open_ports.sort(key=lambda x: x["port"])
    return open_ports
