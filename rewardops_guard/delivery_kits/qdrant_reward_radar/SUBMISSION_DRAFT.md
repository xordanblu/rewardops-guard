# Qdrant Hackathon Submission Draft

## Project

Qdrant Reward Route Radar

## Short Description

A non-chatbot Qdrant application that ranks reward opportunities by semantic fit, payout size, risk, and safety constraints so an operator can pursue real-money routes without leaking secrets, using social accounts, or confusing pending work with earned revenue.

## What It Does

The demo indexes a synthetic set of hackathons, gigs, and unsafe bounty fixtures in Qdrant. A deterministic local embedding function creates vectors for each opportunity, while Qdrant payload filters enforce hard constraints such as no social-account requirements, no wallet signing, and no secret disclosure. The output is a ranked action queue with next steps.

## Why Qdrant Matters

Qdrant is used as the vector index and payload filter engine. The demo combines semantic matching with structured filters for reward amount, risk, and safety flags. This goes beyond a chatbot because the interface is a ranking and decision surface for operational triage.

## Demo Script

1. Open the local web demo at `http://127.0.0.1:8787`.
2. Show the sample opportunity dataset and the unsafe fixtures.
3. Run the default high-upside query.
4. Show Qdrant returning `qdrant-vsd-2026` while excluding social and prompt-exfiltration routes.
5. Change minimum reward, maximum risk, and review-mode controls to show how filters reshape the action queue.
6. Show the preflight report and external submission gates.

## Links To Prepare

- GitHub repo: `https://github.com/xordanx/rewardops-guard`
- Package path: `rewardops_guard/delivery_kits/qdrant_reward_radar`
- Local web demo command: `/tmp/qdrant-radar-venv/bin/python -m rewardops_guard.delivery_kits.qdrant_reward_radar.web_demo --host 127.0.0.1 --port 8787`
- Video script: `rewardops_guard/delivery_kits/qdrant_reward_radar/VIDEO_SCRIPT.md`
- Demo video: hold until explicitly approved and recorded.

## External Gates

Do not submit externally until registration, GitHub sharing, video hosting, and prize-documentation implications are approved.
