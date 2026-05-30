# Qdrant Reward Route Radar

Non-chatbot vector search demo for Qdrant's "Think Outside the Bot" virtual hackathon.

The app indexes reward opportunities in Qdrant, embeds each opportunity with a deterministic local feature vector, applies payload filters for safety constraints, and ranks the next best route by technical fit, payout size, risk, and deadline pressure.

## Why It Fits

- Qdrant is the material search layer: opportunities are stored as vector points with payload filters.
- The interaction is not a chatbot: it is an operator dashboard/CLI that ranks actions and blocks unsafe routes.
- The demo uses vector search beyond Q&A: reward-route triage, safety gating, and payout-focused prioritization.
- It uses a public, synthetic dataset so no private account data, social accounts, wallet signatures, PHI, or secrets are required.

## Run

```bash
python3 -m venv /tmp/qdrant-radar-venv
/tmp/qdrant-radar-venv/bin/python -m pip install -r rewardops_guard/delivery_kits/qdrant_reward_radar/requirements.txt
/tmp/qdrant-radar-venv/bin/python -m rewardops_guard.delivery_kits.qdrant_reward_radar.reward_radar --min-reward 1000 --allow-review --json
/tmp/qdrant-radar-venv/bin/python -m rewardops_guard.delivery_kits.qdrant_reward_radar.contest_preflight
```

Dependency-free unit checks still run without `qdrant-client`; the Qdrant integration test is skipped unless the client is installed.

```bash
python3 -m unittest rewardops_guard.delivery_kits.qdrant_reward_radar.test_reward_radar -v
```

## Demo Query

```bash
/tmp/qdrant-radar-venv/bin/python -m rewardops_guard.delivery_kits.qdrant_reward_radar.reward_radar \
  --query "non-chatbot vector search hackathon with safety ranking" \
  --min-reward 1000 \
  --allow-review
```

Expected top route: `qdrant-vsd-2026`, while social-account and prompt-exfiltration fixtures are filtered out. Routes that might require prize paperwork later are kept in review mode instead of being treated as safe to execute automatically.

## Local Web Demo

```bash
/tmp/qdrant-radar-venv/bin/python -m rewardops_guard.delivery_kits.qdrant_reward_radar.web_demo --host 127.0.0.1 --port 8787
```

Open `http://127.0.0.1:8787`. The web demo exposes the same Qdrant-backed ranking API at `/api/search`, with controls for intent, minimum reward, maximum risk, and review-mode routing.

## Demo Video Prep

`VIDEO_SCRIPT.md` contains the walkthrough script. A local rendered MP4 is available in `demo_video/renders/qdrant_reward_route_radar_demo.mp4`, with validation details in `demo_video/VIDEO_MANIFEST.md`.

```bash
cd rewardops_guard/delivery_kits/qdrant_reward_radar/demo_video
npm run check
npm run render -- --output renders/qdrant_reward_route_radar_demo.mp4 --quality draft --fps 24 --workers 1
```

External video upload is intentionally held until submission approval.

## Submission Gate

This repository package is local-only until these external steps are explicitly approved:

- Register for the Qdrant hackathon.
- Publish or share the GitHub repository with organizers.
- Record and host a demo video no longer than 3 minutes.
- Submit through the Qdrant form before the deadline.
- Provide prize identity/payment documents only if selected.
