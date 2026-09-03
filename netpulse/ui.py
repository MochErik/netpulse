"""Terminal styling and formatted output rendering for NetPulse CLI."""

from typing import List, Dict, Any

# ANSI Color Codes for zero-dependency terminal styling
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
WHITE = "\033[37m"


def print_banner():
    banner = f"""
{CYAN}{BOLD}⚡ NetPulse{RESET} {DIM}v1.0.0 — Modern Network & DNS Diagnostic Suite{RESET}
{DIM}Crafted by Moch. Erik Irriansyah | High-Performance Network Analyzer{RESET}
─────────────────────────────────────────────────────────────"""
    print(banner)


def render_ip_info(info: Dict[str, Any]):
    print(f"\n{BOLD}🌐 Public Network & ISP Identity:{RESET}")
    print(f"  {CYAN}• Public IP   :{RESET} {BOLD}{info.get('ip', 'N/A')}{RESET}")
    print(f"  {CYAN}• ISP / ASN   :{RESET} {info.get('org', 'N/A')} ({info.get('asn', 'N/A')})")
    print(f"  {CYAN}• Location    :{RESET} {info.get('city', 'N/A')}, {info.get('region', 'N/A')}, {info.get('country', 'N/A')}")
    print(f"  {CYAN}• Timezone    :{RESET} {info.get('timezone', 'N/A')}")


def render_ping_mesh(results: List[Dict[str, Any]]):
    print(f"\n{BOLD}📡 Multi-Target Latency & Ping Mesh:{RESET}")
    print(f"{'Target Name':<24} {'Host / IP':<18} {'Status':<10} {'Avg RTT':<12} {'Loss %':<8} {'Jitter':<10}")
    print("─" * 86)
    
    for r in results:
        status_color = GREEN if r["status"] == "online" else RED
        status_text = f"{status_color}{r['status'].upper()}{RESET}"
        
        avg_str = f"{r['avg_ms']:.1f} ms" if r.get("avg_ms") is not None else "-"
        jitter_str = f"{r['jitter_ms']:.1f} ms" if r.get("jitter_ms") is not None else "-"
        loss_str = f"{r.get('packet_loss', 0):.0f}%"
        
        # Highlight fast vs slow latencies
        if r.get("avg_ms") is not None:
            if r["avg_ms"] < 25:
                avg_str = f"{GREEN}{avg_str}{RESET}"
            elif r["avg_ms"] < 80:
                avg_str = f"{YELLOW}{avg_str}{RESET}"
            else:
                avg_str = f"{RED}{avg_str}{RESET}"

        print(f"{r['name']:<24} {r['host']:<18} {status_text:<19} {avg_str:<21} {loss_str:<8} {jitter_str:<10}")


def render_dns_benchmark(results: List[Dict[str, Any]]):
    print(f"\n{BOLD}⚡ DNS Resolver Benchmark (Speed & Reliability):{RESET}")
    print(f"{'Rank':<5} {'Resolver Provider':<22} {'IP Address':<16} {'Avg Latency':<14} {'Min / Max':<16} {'Reliability':<12}")
    print("─" * 88)
    
    for idx, r in enumerate(results, start=1):
        rank_badge = f"{BOLD}#{idx}{RESET}"
        avg_str = f"{r['avg_ms']:.1f} ms" if r["avg_ms"] is not None else "Timeout"
        
        if r["avg_ms"] is not None:
            if r["avg_ms"] < 20:
                avg_str = f"{GREEN}{BOLD}{avg_str}{RESET}"
            elif r["avg_ms"] < 50:
                avg_str = f"{CYAN}{avg_str}{RESET}"
            elif r["avg_ms"] < 100:
                avg_str = f"{YELLOW}{avg_str}{RESET}"
            else:
                avg_str = f"{RED}{avg_str}{RESET}"

        min_max_str = f"{r['min_ms']:.1f} / {r['max_ms']:.1f} ms" if r["min_ms"] is not None else "-"
        rel_color = GREEN if r["reliability"] == 100 else (YELLOW if r["reliability"] >= 80 else RED)
        rel_str = f"{rel_color}{r['reliability']}%{RESET}"
        
        print(f"{rank_badge:<13} {r['name']:<22} {r['ip']:<16} {avg_str:<23} {min_max_str:<16} {rel_str:<20}")


def render_port_scan(target: str, open_ports: List[Dict[str, Any]]):
    print(f"\n{BOLD}🔍 Open Ports & Service Discovery on {CYAN}{target}{RESET}:{RESET}")
    if not open_ports:
        print(f"  {YELLOW}No common open ports discovered or target firewall active.{RESET}")
        return

    print(f"{'Port':<8} {'State':<10} {'Service':<18} {'Banner / Identification':<35}")
    print("─" * 75)
    for p in open_ports:
        port_badge = f"{GREEN}{p['port']}/TCP{RESET}"
        state = f"{GREEN}OPEN{RESET}"
        banner = p.get("banner") or "-"
        print(f"{port_badge:<17} {state:<19} {p['service']:<18} {banner:<35}")
