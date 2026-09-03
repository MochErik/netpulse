# ⚡ NetPulse (`netpulse-cli`)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![100% Local CLI](https://img.shields.io/badge/Architecture-100%25%20Local%20CLI-brightgreen.svg)](https://github.com/MochErik/netpulse)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange.svg)](https://github.com/MochErik/netpulse)

> **High-Performance Multi-Target Latency Mesh, DNS Benchmark & Port Scanner CLI.** Diagnostic suite designed for network engineers and sysadmins with zero external dependencies.

---

## 🌟 Fitur Utama
- 📡 **Multi-Target Latency Mesh**: Mengukur latensi RTT, jitter, dan packet loss terhadap Cloudflare, Google DNS, GitHub, dan default gateway secara bersamaan.
- ⚡ **Wire-Format DNS Benchmark**: Mengirim paket UDP raw DNS langsung ke resolver upstream (Cloudflare, Quad9, Google, AdGuard) untuk membandingkan kecepatan respons.
- 🔍 **High-Speed Port Scanner**: Memindai port TCP terbuka secara konkruen disertai identifikasi service dan *banner grabbing*.
- 🌐 **ISP & GeoIP Identity**: Deteksi IP publik, nomor ASN, nama organisasi ISP, dan lokasi geografis.
- 📊 **JSON Export**: Output terstruktur (`--json`) untuk integrasi skrip otomasi.

---

## 🚀 Quick Install
```bash
pip install git+https://github.com/MochErik/netpulse.git
```

---

## 🖥️ Contoh Penggunaan
```bash
# Diagnosa lengkap (GeoIP + Ping Mesh + DNS Benchmark)
netpulse

# Benchmark DNS resolver saja
netpulse --dns

# Scan port terbuka di router / IP lokal
netpulse --scan 192.168.1.1

# Ekspor format JSON
netpulse --json
```

---

## 📜 License
MIT License © 2026 [Moch. Erik Irriansyah](https://github.com/MochErik)
