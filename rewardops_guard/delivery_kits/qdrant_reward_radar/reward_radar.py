#!/usr/bin/env python3
"""Vector-search reward-route radar for the Qdrant hackathon route.

This is intentionally not a chatbot. It is a deterministic ranking surface that
uses Qdrant as the vector index and payload filter engine for reward
opportunities.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, Range, VectorParams
except Exception:  # pragma: no cover - exercised by preflight when dependency is absent
    QdrantClient = None  # type: ignore[assignment]
    Distance = FieldCondition = Filter = MatchValue = PointStruct = Range = VectorParams = None  # type: ignore[assignment]


KIT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = KIT_ROOT / "sample_opportunities.json"
COLLECTION = "reward_route_radar"
VECTOR_SIZE = 96
BLOCKED_FLAGS = ("requires_social", "requires_wallet_signing", "requires_secret_disclosure")
REVIEW_FLAGS = ("requires_kyc",)


@dataclass(frozen=True)
class RankedRoute:
    route_id: str
    title: str
    reward_usd: float
    score: float
    risk_level: int
    deadline: str
    url: str
    action: str


def load_opportunities(path: Path = DEFAULT_DATASET) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def token_stream(text: str) -> Iterable[str]:
    normalized = "".join(char.lower() if char.isalnum() else " " for char in text)
    words = [word for word in normalized.split() if word]
    for word in words:
        yield word
        if len(word) > 3:
            for index in range(len(word) - 2):
                yield word[index : index + 3]


def embed_text(text: str, dimensions: int = VECTOR_SIZE) -> list[float]:
    vector = [0.0] * dimensions
    for token in token_stream(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        sign = -1.0 if digest[4] & 1 else 1.0
        vector[bucket] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def opportunity_text(opportunity: dict[str, Any]) -> str:
    skills = " ".join(opportunity.get("skills", []))
    return f"{opportunity['title']} {opportunity['source']} {skills} {opportunity['summary']}"


def safety_decision(opportunity: dict[str, Any]) -> dict[str, Any]:
    blockers = [flag for flag in BLOCKED_FLAGS if opportunity.get(flag)]
    review_flags = [flag for flag in REVIEW_FLAGS if opportunity.get(flag)]
    risk_level = int(opportunity.get("risk_level", 0))
    if blockers or risk_level >= 8:
        decision = "BLOCK"
    elif review_flags or risk_level >= 4:
        decision = "REVIEW"
    else:
        decision = "ALLOW"
    return {
        "decision": decision,
        "blockers": blockers,
        "review_flags": review_flags,
        "risk_level": risk_level,
    }


def require_qdrant() -> None:
    if QdrantClient is None:
        raise RuntimeError("qdrant-client is required. Install with: python3 -m pip install -r requirements.txt")


def build_client(location: str = ":memory:"):
    require_qdrant()
    return QdrantClient(location)


def recreate_collection(client: Any, collection_name: str = COLLECTION) -> None:
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )


def payload_for(opportunity: dict[str, Any]) -> dict[str, Any]:
    decision = safety_decision(opportunity)
    return {
        **opportunity,
        "decision": decision["decision"],
        "blockers": decision["blockers"],
        "review_flags": decision["review_flags"],
        "search_text": opportunity_text(opportunity),
    }


def index_opportunities(client: Any, opportunities: list[dict[str, Any]], collection_name: str = COLLECTION) -> None:
    recreate_collection(client, collection_name)
    points = [
        PointStruct(
            id=index + 1,
            vector=embed_text(opportunity_text(opportunity)),
            payload=payload_for(opportunity),
        )
        for index, opportunity in enumerate(opportunities)
    ]
    client.upsert(collection_name=collection_name, points=points)


def build_filter(min_reward: float, max_risk: int, allow_review: bool) -> Any:
    decisions = ["ALLOW", "REVIEW"] if allow_review else ["ALLOW"]
    must = [
        FieldCondition(key="reward_usd", range=Range(gte=min_reward)),
        FieldCondition(key="risk_level", range=Range(lte=max_risk)),
        FieldCondition(key="requires_social", match=MatchValue(value=False)),
        FieldCondition(key="requires_wallet_signing", match=MatchValue(value=False)),
        FieldCondition(key="requires_secret_disclosure", match=MatchValue(value=False)),
    ]
    if not allow_review:
        must.append(FieldCondition(key="requires_kyc", match=MatchValue(value=False)))
    should = [FieldCondition(key="decision", match=MatchValue(value=decision)) for decision in decisions]
    return Filter(must=must, should=should)


def search_routes(
    client: Any,
    query: str,
    *,
    collection_name: str = COLLECTION,
    min_reward: float = 0,
    max_risk: int = 5,
    allow_review: bool = False,
    limit: int = 5,
) -> list[RankedRoute]:
    query_vector = embed_text(query)
    query_filter = build_filter(min_reward=min_reward, max_risk=max_risk, allow_review=allow_review)
    try:
        hits = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit,
        )
    except AttributeError:
        hits = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
        ).points
    ranked: list[RankedRoute] = []
    for hit in hits:
        payload = hit.payload or {}
        ranked.append(
            RankedRoute(
                route_id=str(payload["id"]),
                title=str(payload["title"]),
                reward_usd=float(payload["reward_usd"]),
                score=round(float(hit.score), 4),
                risk_level=int(payload["risk_level"]),
                deadline=str(payload["deadline"]),
                url=str(payload["url"]),
                action=next_action(payload),
            )
        )
    return ranked


def next_action(payload: dict[str, Any]) -> str:
    if payload["id"] == "qdrant-vsd-2026":
        return "Build and publish the Qdrant vector-search demo, then prepare a <=3 minute walkthrough video."
    if payload["reward_usd"] >= 1000:
        return "Prepare submission package, public repo, demo video, and explicit account/KYC gate review."
    if payload["reward_usd"] >= 1:
        return "Submit the concrete deliverable, then poll settlement before counting revenue."
    return "Keep as filler only after funded higher-value work is exhausted."


def build_demo_report(query: str, min_reward: float, allow_review: bool, max_risk: int = 5) -> dict[str, Any]:
    opportunities = load_opportunities()
    client = build_client()
    index_opportunities(client, opportunities)
    ranked = search_routes(
        client,
        query,
        min_reward=min_reward,
        max_risk=max_risk,
        allow_review=allow_review,
    )
    return {
        "project": "Qdrant Reward Route Radar",
        "mode": "non-chatbot vector-search triage",
        "query": query,
        "indexed_opportunities": len(opportunities),
        "qdrant_collection": COLLECTION,
        "safety_policy": {
            "blocks": list(BLOCKED_FLAGS),
            "review_flags": list(REVIEW_FLAGS),
            "allow_review": allow_review,
            "min_reward_usd": min_reward,
            "max_risk": max_risk,
        },
        "ranked_routes": [route.__dict__ for route in ranked],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank reward routes with Qdrant vector search.")
    parser.add_argument("--query", default="high upside vector search hackathon no chatbot safe public repo")
    parser.add_argument("--min-reward", type=float, default=0)
    parser.add_argument("--max-risk", type=int, default=5)
    parser.add_argument("--allow-review", action="store_true", help="Allow non-blocked routes that still need external review.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = build_demo_report(args.query, args.min_reward, args.allow_review, max_risk=args.max_risk)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"{report['project']} ({report['mode']})")
        for index, route in enumerate(report["ranked_routes"], start=1):
            print(f"{index}. ${route['reward_usd']:.0f} {route['title']} score={route['score']} risk={route['risk_level']}")
            print(f"   {route['action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
