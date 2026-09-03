"""NetPulse CLI Main Entrypoint."""

import argparse
import json
import sys
from typing import List

from netpulse.ping_mesh import run_ping_mesh
from netpulse.dns_bench import run_dns_benchmark
from netpulse.port_scan import scan_target_ports
from netpulse.geo_ip import fetch_ip_info
from netpulse.ui import (
    print_banner,
    render_ip_info,
    render_ping_mesh,
    render_dns_benchmark,
    render_port_scan,
)


def main(args: List[str] = None):
    parser = argparse.ArgumentParser(
        prog="netpulse",
        description="⚡ NetPulse - High-Performance Network & DNS Diagnostic Suite CLI",
        epilog="Examples:\n"
               "  netpulse                  # Run full diagnostic sweep (GeoIP, Ping Mesh, DNS Bench)\n"
               "  netpulse --ping           # Measure multi-target ping & jitter\n"
               "  netpulse --dns            # Benchmark DNS resolvers response time\n"
               "  netpulse --scan 192.168.1.1 # Scan common open ports on target\n"
               "  netpulse --ip             # Show public IP, ASN & Geo-location\n"
               "  netpulse --json           # Export all diagnostics in JSON format\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--ping", action="store_true", help="Run ping mesh & latency diagnostic")
    parser.add_argument("--dns", action="store_true", help="Benchmark top DNS resolvers")
    parser.add_argument("--scan", type=str, metavar="HOST", help="Scan open TCP ports on specified host")
    parser.add_argument("--ip", action="store_true", help="Inspect public IP & ASN info")
    parser.add_argument("--target", "-t", action="append", help="Add custom target to ping test")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--version", "-v", action="version", version="netpulse 1.0.0")

    parsed = parser.parse_args(args)

    # If no specific mode flag provided, default to full sweep
    run_all = not (parsed.ping or parsed.dns or parsed.scan or parsed.ip)

    data = {}

    if parsed.json:
        # JSON silent mode
        if run_all or parsed.ip:
            data["ip_info"] = fetch_ip_info()
        if run_all or parsed.ping:
            data["ping_mesh"] = run_ping_mesh(custom_targets=parsed.target)
        if run_all or parsed.dns:
            data["dns_bench"] = run_dns_benchmark()
        if parsed.scan:
            data["port_scan"] = {
                "target": parsed.scan,
                "open_ports": scan_target_ports(parsed.scan)
            }
        print(json.dumps(data, indent=2))
        return

    # Interactive Colored TUI
    print_banner()

    if run_all or parsed.ip:
        print("🔍 Discovering Public IP and ISP ASN metadata...")
        ip_info = fetch_ip_info()
        render_ip_info(ip_info)

    if run_all or parsed.ping:
        print("\n⏳ Testing ICMP / TCP Round-Trip Latency & Jitter...")
        ping_results = run_ping_mesh(custom_targets=parsed.target)
        render_ping_mesh(ping_results)

    if run_all or parsed.dns:
        print("\n⏳ Benchmarking DNS lookup response times across upstream providers...")
        dns_results = run_dns_benchmark()
        render_dns_benchmark(dns_results)

    if parsed.scan:
        print(f"\n⏳ Probing common services and ports on {parsed.scan}...")
        open_ports = scan_target_ports(parsed.scan)
        render_port_scan(parsed.scan, open_ports)

    print("\n✅ Diagnostic sweep completed successfully.\n")


if __name__ == "__main__":
    main()
