from __future__ import annotations

import unittest

from submission import devpost_preflight


class DevpostPreflightTests(unittest.TestCase):
    def test_local_preflight_is_ready_but_external_submission_is_blocked_without_video(self) -> None:
        report = devpost_preflight.build_preflight(devpost_preflight.ROOT)

        self.assertTrue(report["local_ok"])
        self.assertFalse(report["external_submission_ok"])
        self.assertEqual(report["status"], "ready_for_external_submission")
        self.assertTrue(any(item["requirement"] == "youtube_vimeo_or_youku_video_url" for item in report["external_blocking"]))
        self.assertFalse(report["local_blocking"])

    def test_video_url_satisfies_video_host_requirement(self) -> None:
        report = devpost_preflight.build_preflight(devpost_preflight.ROOT, "https://youtu.be/example")
        video_check = next(item for item in report["checks"] if item["requirement"] == "youtube_vimeo_or_youku_video_url")

        self.assertTrue(video_check["ok"])
        self.assertTrue(any(item["requirement"] == "devpost_form_submission" for item in report["external_blocking"]))


if __name__ == "__main__":
    unittest.main()
