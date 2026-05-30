from __future__ import annotations

import unittest

from rewardops_guard.delivery_kits.qdrant_reward_radar import reward_radar
from rewardops_guard.delivery_kits.qdrant_reward_radar import web_demo
from rewardops_guard.delivery_kits.qdrant_reward_radar import contest_preflight


class RewardRadarTests(unittest.TestCase):
    def test_embedding_is_deterministic_and_normalized(self) -> None:
        first = reward_radar.embed_text("Qdrant vector search reward radar")
        second = reward_radar.embed_text("Qdrant vector search reward radar")
        self.assertEqual(first, second)
        self.assertEqual(len(first), reward_radar.VECTOR_SIZE)
        self.assertAlmostEqual(sum(value * value for value in first), 1.0)

    def test_safety_decision_blocks_disallowed_routes(self) -> None:
        social = {"requires_social": True, "requires_kyc": False, "requires_wallet_signing": False, "requires_secret_disclosure": False, "risk_level": 2}
        secret = {"requires_social": False, "requires_kyc": False, "requires_wallet_signing": False, "requires_secret_disclosure": True, "risk_level": 2}
        kyc = {"requires_social": False, "requires_kyc": True, "requires_wallet_signing": False, "requires_secret_disclosure": False, "risk_level": 2}
        safe = {"requires_social": False, "requires_kyc": False, "requires_wallet_signing": False, "requires_secret_disclosure": False, "risk_level": 1}
        self.assertEqual(reward_radar.safety_decision(social)["decision"], "BLOCK")
        self.assertEqual(reward_radar.safety_decision(secret)["decision"], "BLOCK")
        self.assertEqual(reward_radar.safety_decision(kyc)["decision"], "REVIEW")
        self.assertEqual(reward_radar.safety_decision(safe)["decision"], "ALLOW")

    @unittest.skipIf(reward_radar.QdrantClient is None, "qdrant-client is not installed")
    def test_qdrant_ranks_vector_hackathon_and_filters_unsafe_routes(self) -> None:
        client = reward_radar.build_client()
        opportunities = reward_radar.load_opportunities()
        reward_radar.index_opportunities(client, opportunities)
        ranked = reward_radar.search_routes(
            client,
            "non-chatbot vector search hackathon with safety ranking",
            min_reward=1000,
            max_risk=5,
            allow_review=True,
        )
        ids = [route.route_id for route in ranked]
        self.assertIn("qdrant-vsd-2026", ids)
        self.assertIn("google-rapid-agent-2026", ids)
        self.assertNotIn("unsafe-instruction-leak-bounty", ids)
        self.assertNotIn("social-growth-bounty", ids)

    @unittest.skipIf(reward_radar.QdrantClient is None, "qdrant-client is not installed")
    def test_web_demo_payload_exposes_ranked_routes_and_blocked_fixtures(self) -> None:
        payload = web_demo.build_search_payload(
            {
                "query": "non-chatbot vector search hackathon with safety ranking",
                "min_reward": "1000",
                "max_risk": "5",
                "allow_review": "true",
            }
        )
        ids = [route["route_id"] for route in payload["ranked_routes"]]
        self.assertIn("qdrant-vsd-2026", ids)
        self.assertIn("google-rapid-agent-2026", ids)
        self.assertIn("unsafe-instruction-leak-bounty", payload["blocked_fixture_ids"])
        self.assertIn("social-growth-bounty", payload["blocked_fixture_ids"])
        self.assertNotIn("google-rapid-agent-2026", payload["blocked_fixture_ids"])

    def test_web_demo_page_has_controls_without_external_assets(self) -> None:
        html = web_demo.render_page()
        self.assertIn("Qdrant Reward Route Radar", html)
        self.assertIn("/api/search", html)
        self.assertNotIn("https://", html)

    @unittest.skipIf(reward_radar.QdrantClient is None, "qdrant-client is not installed")
    def test_preflight_tracks_rendered_video_artifacts(self) -> None:
        report = contest_preflight.build_report()
        self.assertTrue(report["video_ok"])
        self.assertTrue(report["web_demo_ok"])
        self.assertTrue(report["local_ok"])


if __name__ == "__main__":
    unittest.main()
