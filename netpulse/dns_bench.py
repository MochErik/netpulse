"""DNS Benchmark module to measure lookup resolution time and reliability across resolvers."""

import socket
import time
import struct
import concurrent.futures
from typing import List, Dict, Any

POPULAR_RESOLVERS = [
    {"name": "Cloudflare Primary", "ip": "1.1.1.1", "provider": "Cloudflare"},
    {"name": "Cloudflare Secondary", "ip": "1.0.0.1", "provider": "Cloudflare"},
    {"name": "Google DNS 1", "ip": "8.8.8.8", "provider": "Google"},
    {"name": "Google DNS 2", "ip": "8.8.4.4", "provider": "Google"},
    {"name": "Quad9 Secure", "ip": "9.9.9.9", "provider": "Quad9"},
    {"name": "OpenDNS Home", "ip": "208.67.222.222", "provider": "Cisco"},
    {"name": "AdGuard Public", "ip": "94.140.14.14", "provider": "AdGuard"},
    {"name": "Control D Uncensored", "ip": "76.76.2.0", "provider": "Control D"}
]

TEST_DOMAINS = ["google.com", "github.com", "cloudflare.com", "wikipedia.org", "netflix.com"]


def build_dns_query_payload(domain: str) -> bytes:
    """Build a standard wire-format raw DNS A-record query packet."""
    # Transaction ID (2 bytes), Flags: standard query 0x0100 (2 bytes)
    # Questions: 1 (2 bytes), Answer RRs: 0, Authority RRs: 0, Additional RRs: 0
    header = struct.pack(">HHHHHH", 0x1337, 0x0100, 1, 0, 0, 0)
    
    question = b""
    for part in domain.split("."):
        encoded = part.encode("ascii")
        question += bytes([len(encoded)]) + encoded
    question += b"\x00"  # Root null byte
    
    # QTYPE: 1 (A record), QCLASS: 1 (IN)
    question += struct.pack(">HH", 1, 1)
    return header + question


def query_dns_server(server_ip: str, domain: str, timeout_sec: float = 1.5) -> Dict[str, Any]:
    """Send UDP DNS query directly to server IP and measure precise resolution round-trip latency."""
    query = build_dns_query_payload(domain)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout_sec)
    
    start = time.perf_counter()
    try:
        sock.sendto(query, (server_ip, 53))
        data, _ = sock.recvfrom(1024)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        sock.close()
        
        # Verify transaction ID match and response code
        if len(data) >= 12:
            rcode = data[3] & 0x0F
            status = "ok" if rcode == 0 else f"rcode_{rcode}"
        else:
            status = "invalid_packet"
            
        return {"domain": domain, "latency_ms": round(elapsed_ms, 2), "success": True, "status": status}
    except socket.timeout:
        sock.close()
        return {"domain": domain, "latency_ms": None, "success": False, "status": "timeout"}
    except Exception as e:
        sock.close()
        return {"domain": domain, "latency_ms": None, "success": False, "status": str(e)}


def benchmark_resolver(resolver: Dict[str, str], domains: List[str]) -> Dict[str, Any]:
    """Benchmark a single DNS resolver across a list of test domains."""
    latencies = []
    successes = 0
    for domain in domains:
        res = query_dns_server(resolver["ip"], domain)
        if res["success"] and res["latency_ms"] is not None:
            latencies.append(res["latency_ms"])
            successes += 1
            
    avg_ms = round(sum(latencies) / len(latencies), 2) if latencies else None
    min_ms = round(min(latencies), 2) if latencies else None
    max_ms = round(max(latencies), 2) if latencies else None
    reliability = round((successes / len(domains)) * 100, 1) if domains else 0.0
    
    return {
        "name": resolver["name"],
        "ip": resolver["ip"],
        "provider": resolver["provider"],
        "avg_ms": avg_ms,
        "min_ms": min_ms,
        "max_ms": max_ms,
        "reliability": reliability,
        "samples": len(latencies)
    }


def run_dns_benchmark(resolvers: List[Dict[str, str]] = None, domains: List[str] = None) -> List[Dict[str, Any]]:
    """Run concurrent DNS benchmarks across all resolvers."""
    resolvers = resolvers or POPULAR_RESOLVERS
    domains = domains or TEST_DOMAINS
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(resolvers)) as executor:
        future_map = {executor.submit(benchmark_resolver, r, domains): r for r in resolvers}
        for f in concurrent.futures.as_completed(future_map):
            results.append(f.result())
            
    # Sort from fastest avg latency to slowest
    results.sort(key=lambda x: (x["avg_ms"] if x["avg_ms"] is not None else 99999))
    return results
