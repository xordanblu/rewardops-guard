#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest

from rewardops_guard.hackathon_submission_builder import build_packet


class HackathonSubmissionBuilderTests(unittest.TestCase):
    def test_keeps_external_actions_held(self) -> None:
        packet = build_packet()
        self.assertGreaterEqual(len(packet["routes"]), 5)
        self.assertTrue(all(route["external_action_gate"] == "HOLD_PUBLIC_SUBMISSION" for route in packet["routes"]))
        self.assertTrue(all(route["may_prepare_local"] for route in packet["routes"]))

    def test_prioritizes_five_k_plus_cash_routes(self) -> None:
        packet = build_packet()
        top_ids = [route["id"] for route in packet["routes"][:4]]
        self.assertIn("google_rapid_agent", top_ids)
        self.assertIn("find_evil", top_ids)
        self.assertTrue(any(route["target_prize_usd"] >= 5000 for route in packet["routes"][:3]))

    def test_does_not_turn_pending_or_inbound_into_revenue_claim(self) -> None:
        packet = build_packet()
        serialized = json.dumps(packet, sort_keys=True).lower()
        self.assertIn("evidence only", serialized)
        self.assertIn("confirmed_revenue_usd", serialized)
        self.assertNotIn("api_key", serialized)
        self.assertNotIn("claimcode", serialized)

    def test_includes_current_hedera_week_two_route(self) -> None:
        packet = build_packet()
        routes = {route["id"]: route for route in packet["routes"]}
        self.assertIn("hedera_enterprise_policy_plugin", routes)
        self.assertEqual(routes["hedera_enterprise_policy_plugin"]["track"], "Week 2 Enterprise Agent + Plugin")
        self.assertIn("hedera_enterprise_policy_plugin/src/policy.js", routes["hedera_enterprise_policy_plugin"]["local_artifacts"])

    def test_find_evil_route_includes_defender_demo_artifacts(self) -> None:
        packet = build_packet()
        routes = {route["id"]: route for route in packet["routes"]}
        self.assertIn("find_evil", routes)
        self.assertIn("rewardops_guard/find_evil_defender_demo.py", routes["find_evil"]["local_artifacts"])
        self.assertIn(
            "rewardops_guard/find_evil_defender_report.md",
            packet["evidence"]["artifact_refs"],
        )


if __name__ == "__main__":
    unittest.main()
