#!/usr/bin/env python3
from __future__ import annotations

import unittest

from rewardops_guard.revenue_evidence_pack import build_pack


class RevenueEvidencePackTests(unittest.TestCase):
    def test_does_not_count_inbound_as_revenue(self) -> None:
        pack = build_pack()
        self.assertIn("confirmed_revenue_usd", pack)
        self.assertGreaterEqual(pack["inbound_market_surface_usd"], pack["confirmed_revenue_usd"])
        self.assertIn("not revenue", pack["revenue_counting_policy"].lower())
        self.assertIn("agentpact", pack)
        self.assertGreaterEqual(pack["agentpact"]["active_offer_usd"], 0)

    def test_tracks_submission_gaps(self) -> None:
        pack = build_pack()
        gaps = " ".join(pack["xprize_readiness"]["gaps_before_submission"]).lower()
        self.assertIn("revenue", gaps)
        self.assertIn("customer", gaps)
        self.assertTrue(pack["xprize_readiness"]["local_prepare_only"])

    def test_top_level_submitted_pending_honors_bountybook_failed_audit(self) -> None:
        pack = build_pack()
        self.assertEqual(
            pack["submitted_pending_verification_usd"],
            pack["bountybook"]["submitted_pending_verification_usd"],
        )


if __name__ == "__main__":
    unittest.main()
