# ⚡ NetPulse (`netpulse-cli`)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![Platform: Linux | macOS | Windows](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/erikirriansyah/netpulse)
[![Zero-Dependency](https://img.shields.io/badge/Dependencies-Zero%20External-orange.svg)](https://github.com/erikirriansyah/netpulse)

> **High-Performance Network & DNS Diagnostic Suite CLI** for Linux, macOS, and Windows. Engineered with zero heavy runtime dependencies, high-concurrency threading, and a rich terminal dashboard.

---

## 🌟 Features

- 📡 **Multi-Target Ping Mesh**: Measures concurrent ICMP/TCP latency, packet loss, and jitter across global DNS, CDNs, and your local default gateway.
- ⚡ **Upstream DNS Benchmark**: Sends wire-format raw DNS packets to Cloudflare, Google, Quad9, AdGuard, OpenDNS, and Control D to find the fastest resolver for your ISP.
- 🔍 **High-Speed Port Scanner**: Concurrent TCP port scanner with service identification and HTTP/SSH banner grabbing.
- 🌐 **ISP & Geolocation Identity**: Discovers public IP, Autonomous System Number (ASN), ISP organization, and location coordinates.
- 📊 **JSON Silent Export**: Seamlessly pipe structured diagnostic reports into `jq`, shell scripts, or Prometheus exporters.

---

## 🚀 Quick Installation

### Option 1: Install via `pip`
```bash
pip install netpulse-cli
```

### Option 2: Run directly via Python (No installation needed)
```bash
git clone https://github.com/erikirriansyah/netpulse.git
cd netpulse
python3 -m netpulse.cli
```

### Option 3: Local Developer Mode
```bash
pip install -e .
```

---

## 🖥️ Usage & Examples

### 1. Full Diagnostic Sweep
Run the complete network health sweep (GeoIP + Ping Mesh + DNS Benchmark):
```bash
netpulse
```

```
⚡ NetPulse v1.0.0 — Modern Network & DNS Diagnostic Suite
Crafted by Moch. Erik Irriansyah | High-Performance Network Analyzer
─────────────────────────────────────────────────────────────

🌐 Public Network & ISP Identity:
  • Public IP   : 180.252.xxx.xxx
  • ISP / ASN   : PT Telkom Indonesia (AS17974)
  • Location    : Surabaya, East Java, Indonesia
  • Timezone    : Asia/Jakarta

📡 Multi-Target Latency & Ping Mesh:
Target Name              Host / IP          Status     Avg RTT      Loss %   Jitter    
──────────────────────────────────────────────────────────────────────────────────
Local Gateway            192.168.1.1        ONLINE     1.4 ms       0%       0.2 ms    
Cloudflare DNS           1.1.1.1            ONLINE     14.2 ms      0%       1.1 ms    
Google Public DNS        8.8.8.8            ONLINE     19.8 ms      0%       1.8 ms    
Quad9 Secure DNS         9.9.9.9            ONLINE     32.5 ms      0%       2.4 ms    
GitHub Edge              github.com         ONLINE     28.1 ms      0%       1.9 ms    

⚡ DNS Resolver Benchmark (Speed & Reliability):
Rank  Resolver Provider      IP Address       Avg Latency    Min / Max        Reliability 
────────────────────────────────────────────────────────────────────────────────────────
#1    Cloudflare Primary     1.1.1.1          12.4 ms        11.1 / 14.2 ms   100%        
#2    Google DNS 1           8.8.8.8          18.6 ms        17.2 / 21.0 ms   100%        
#3    AdGuard Public         94.140.14.14     29.4 ms        27.0 / 33.1 ms   100%        
#4    Quad9 Secure           9.9.9.9          31.8 ms        30.2 / 34.5 ms   100%        
```

### 2. Run Individual Diagnostics

- **Ping Latency Mesh only**:
  ```bash
  netpulse --ping
  ```

- **Ping with Custom Targets**:
  ```bash
  netpulse --ping -t 1.1.1.1 -t 10.0.0.1 -t my-server.com
  ```

- **DNS Speed Benchmark only**:
  ```bash
  netpulse --dns
  ```

- **Scan Open Ports on Local Router / Server**:
  ```bash
  netpulse --scan 192.168.1.1
  ```

- **Inspect Public IP & ASN only**:
  ```bash
  netpulse --ip
  ```

- **Export JSON for Automation / Scripting**:
  ```bash
  netpulse --json | jq .
  ```

---

## 🛠️ Architecture & Philosophy

NetPulse is built with **zero external dependencies** using Python's standard library (`socket`, `struct`, `subprocess`, `concurrent.futures`, `urllib.request`). It works out of the box on lightweight embedded Linux SBCs (Raspberry Pi, Armbian STB HG680P/B860H) as well as heavy servers and developer laptops.

---

## 📜 License

MIT License © 2026 [Moch. Erik Irriansyah](https://github.com/erikirriansyah)
