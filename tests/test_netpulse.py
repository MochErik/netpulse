"""Unit tests for NetPulse CLI suite."""

import unittest
from netpulse.ping_mesh import ping_host, detect_default_gateway, run_ping_mesh
from netpulse.dns_bench import build_dns_query_payload, benchmark_resolver
from netpulse.port_scan import probe_port
from netpulse.geo_ip import fetch_ip_info


class TestNetPulse(unittest.TestCase):

    def test_dns_query_payload_builder(self):
        payload = build_dns_query_payload("google.com")
        self.assertIsInstance(payload, bytes)
        self.assertGreater(len(payload), 12)
        # Check standard transaction ID 0x1337
        self.assertEqual(payload[:2], b"\x13\x37")

    def test_localhost_probe_port(self):
        # Probing an invalid or closed port should not crash
        res = probe_port("127.0.0.1", 65432, timeout_sec=0.2)
        self.assertIn("is_open", res)
        self.assertIn("service", res)

    def test_ping_loopback(self):
        res = ping_host("127.0.0.1", count=1, timeout_sec=1.0)
        self.assertIn("status", res)
        self.assertIn(res["status"], ["online", "offline"])

    def test_geoip_structure(self):
        info = fetch_ip_info(timeout=2.0)
        self.assertIn("ip", info)


if __name__ == "__main__":
    unittest.main()
