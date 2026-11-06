"""Claim extraction and evidence retrieval for VeriFact AI.

Verdicts remain inconclusive unless a configured verifier can compare evidence.
Search results are evidence candidates, not proof.
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any

import httpx


def extract_claims(answer: str) -> list[str]:
    """Split a supplied answer into reviewable sentence/line units."""
    pieces = re.split(r"(?<=[.!?])\s+|\n+", answer.strip())
    return [piece.strip(" •-*\t") for piece in pieces if piece.strip(" •-*\t")]


async def search_evidence(claim: str, max_results: int = 5) -> list[dict[str, Any]]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY is not configured")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": claim,
                "search_depth": "advanced",
                "max_results": max_results,
                "include_answer": False,
                "include_raw_content": False,
            },
        )
        response.raise_for_status()
        payload = response.json()

    retrieved_at = datetime.now(timezone.utc).isoformat()
    evidence = []
    for item in payload.get("results", []):
        evidence.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "snippet": item.get("content"),
            "source_score": item.get("score"),
            "published_date": item.get("published_date"),
            "retrieved_at": retrieved_at,
        })
    return evidence


def initial_temporal_label(claim: str) -> str:
    """Heuristic prioritization only; not a truth verdict."""
    time_sensitive = re.search(
        r"\b(current|currently|latest|today|now|this year|price|pricing|version|release|"
        r"regulation|law|policy|CEO|president|available|deadline|rate)\b",
        claim,
        flags=re.IGNORECASE,
    )
    return "time_sensitive" if time_sensitive else "temporal_sensitivity_unknown"
