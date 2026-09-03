"""Ping Mesh module for multi-target concurrent ICMP and socket latency measurement."""

import socket
import time
import subprocess
import platform
import concurrent.futures
from typing import List, Dict, Any, Optional

DEFAULT_TARGETS = [
    {"name": "Cloudflare DNS", "host": "1.1.1.1", "tag": "DNS / Global"},
    {"name": "Google Public DNS", "host": "8.8.8.8", "tag": "DNS / Global"},
    {"name": "Quad9 Secure DNS", "host": "9.9.9.9", "tag": "DNS / Security"},
    {"name": "OpenDNS Home", "host": "208.67.222.222", "tag": "DNS / Global"},
    {"name": "GitHub Edge", "host": "github.com", "tag": "Web / CDN"},
    {"name": "Google Edge", "host": "google.com", "tag": "Web / Anycast"},
]


def detect_default_gateway() -> Optional[str]:
    """Auto-detect local default gateway IP address."""
    os_name = platform.system().lower()
    try:
        if os_name == "darwin" or "bsd" in os_name:
            out = subprocess.check_output(["route", "-n", "get", "default"], stderr=subprocess.DEVNULL, timeout=2).decode()
            for line in out.splitlines():
                if "gateway:" in line:
                    return line.split("gateway:")[1].strip()
        elif os_name == "linux":
            out = subprocess.check_output(["ip", "route", "show", "default"], stderr=subprocess.DEVNULL, timeout=2).decode()
            parts = out.split()
            if "via" in parts:
                return parts[parts.index("via") + 1]
        elif os_name == "windows":
            out = subprocess.check_output(["tracert", "-d", "-h", "1", "1.1.1.1"], stderr=subprocess.DEVNULL, timeout=3).decode()
            # Windows fallback or parsing
    except Exception:
        pass
    return None


def ping_host(host: str, count: int = 3, timeout_sec: float = 1.0) -> Dict[str, Any]:
    """Ping a host using native OS ping utility for accurate ICMP round-trip latency."""
    os_name = platform.system().lower()
    cmd = []
    
    if os_name == "windows":
        cmd = ["ping", "-n", str(count), "-w", str(int(timeout_sec * 1000)), host]
    elif os_name == "darwin":
        cmd = ["ping", "-c", str(count), "-t", str(int(timeout_sec)), host]
    else:  # Linux / Unix
        cmd = ["ping", "-c", str(count), "-W", str(int(timeout_sec)), host]

    start_time = time.time()
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=(timeout_sec * count) + 2)
        elapsed = time.time() - start_time
        
        output = proc.stdout
        lines = output.splitlines()
        
        # Parse packet loss and rtt
        packet_loss = 100.0
        min_rtt, avg_rtt, max_rtt, mdev_rtt = None, None, None, None
        
        for line in lines:
            if "% packet loss" in line or "% loss" in line:
                for token in line.split(","):
                    if "% packet loss" in token or "% loss" in token:
                        try:
                            packet_loss = float(token.strip().split("%")[0].split()[-1])
                        except Exception:
                            packet_loss = 0.0 if proc.returncode == 0 else 100.0
            
            # Linux: rtt min/avg/max/mdev = 12.34/15.67/18.90/2.11 ms
            # macOS: round-trip min/avg/max/stddev = 12.34/15.67/18.90/2.11 ms
            if "min/avg/max" in line or "round-trip" in line:
                try:
                    stats_part = line.split("=")[1].strip().split()[0]
                    parts = [float(x) for x in stats_part.split("/")]
                    min_rtt, avg_rtt, max_rtt = parts[0], parts[1], parts[2]
                    if len(parts) > 3:
                        mdev_rtt = parts[3]
                except Exception:
                    pass

        # Fallback if parsing failed but command succeeded
        if proc.returncode == 0 and avg_rtt is None:
            avg_rtt = (elapsed / count) * 1000
            min_rtt, max_rtt = avg_rtt, avg_rtt
            packet_loss = 0.0

        return {
            "host": host,
            "status": "online" if (proc.returncode == 0 and packet_loss < 100) else "offline",
            "packet_loss": packet_loss,
            "min_ms": min_rtt,
            "avg_ms": avg_rtt,
            "max_ms": max_rtt,
            "jitter_ms": mdev_rtt or (abs(max_rtt - min_rtt) if (max_rtt and min_rtt) else 0.0),
            "raw_output": output
        }
    except Exception as e:
        # Fallback TCP ping to port 80/443 if ICMP is blocked or failed
        return tcp_ping(host, count=count, timeout_sec=timeout_sec)


def tcp_ping(host: str, port: int = 80, count: int = 3, timeout_sec: float = 1.0) -> Dict[str, Any]:
    """TCP connect latency fallback when ICMP is restricted."""
    latencies = []
    for _ in range(count):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout_sec)
        t0 = time.perf_counter()
        try:
            s.connect((host, port))
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)
            s.close()
        except Exception:
            pass
        time.sleep(0.05)

    if latencies:
        min_rtt = min(latencies)
        max_rtt = max(latencies)
        avg_rtt = sum(latencies) / len(latencies)
        loss = ((count - len(latencies)) / count) * 100.0
        return {
            "host": host,
            "status": "online",
            "packet_loss": loss,
            "min_ms": round(min_rtt, 2),
            "avg_ms": round(avg_rtt, 2),
            "max_ms": round(max_rtt, 2),
            "jitter_ms": round(max_rtt - min_rtt, 2),
            "mode": "tcp"
        }
    return {
        "host": host,
        "status": "offline",
        "packet_loss": 100.0,
        "min_ms": None,
        "avg_ms": None,
        "max_ms": None,
        "jitter_ms": None,
        "mode": "tcp"
    }


def run_ping_mesh(custom_targets: Optional[List[str]] = None, count: int = 3) -> List[Dict[str, Any]]:
    """Run concurrent ping tests across a target mesh including gateway and DNS servers."""
    targets = []
    gateway = detect_default_gateway()
    if gateway:
        targets.append({"name": "Local Gateway", "host": gateway, "tag": "LAN / Router"})

    if custom_targets:
        for t in custom_targets:
            targets.append({"name": t, "host": t, "tag": "Custom Target"})
    else:
        targets.extend(DEFAULT_TARGETS)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(targets), 10)) as executor:
        future_to_target = {executor.submit(ping_host, t["host"], count): t for t in targets}
        for future in concurrent.futures.as_completed(future_to_target):
            target_meta = future_to_target[future]
            try:
                res = future.result()
                res["name"] = target_meta["name"]
                res["tag"] = target_meta["tag"]
                results.append(res)
            except Exception as e:
                results.append({
                    "name": target_meta["name"],
                    "host": target_meta["host"],
                    "tag": target_meta["tag"],
                    "status": "error",
                    "packet_loss": 100.0,
                    "avg_ms": None,
                    "error": str(e)
                })

    # Sort results: LAN first, then by avg latency
    def sort_key(item):
        if item.get("tag", "").startswith("LAN"):
            return -1
        avg = item.get("avg_ms")
        return avg if avg is not None else 99999.0

    results.sort(key=sort_key)
    return results
