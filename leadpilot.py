"""Core logic for Cynbit LeadPilot: transparent lead scoring and safe follow-up drafting."""
from __future__ import annotations

import os
from typing import Any

import pandas as pd
import requests

REQUIRED_COLUMNS = [
    "name", "company", "email", "budget", "interest_level",
    "engagement", "last_contact_days"
]

SAMPLE_ROWS = [
    {"name": "Aarav Mehta", "company": "Northstar Retail", "email": "aarav@example.com", "budget": 18000, "interest_level": "High", "engagement": "High", "last_contact_days": 2},
    {"name": "Diya Rao", "company": "BluePeak Labs", "email": "diya@example.com", "budget": 7000, "interest_level": "Medium", "engagement": "High", "last_contact_days": 5},
    {"name": "Kabir Shah", "company": "Evergreen Foods", "email": "kabir@example.com", "budget": 2500, "interest_level": "Low", "engagement": "Low", "last_contact_days": 35},
    {"name": "Ananya Iyer", "company": "BrightPath Edu", "email": "ananya@example.com", "budget": 12000, "interest_level": "High", "engagement": "Medium", "last_contact_days": 9},
    {"name": "Rohan Kulkarni", "company": "UrbanNest", "email": "rohan@example.com", "budget": 5000, "interest_level": "Medium", "engagement": "Low", "last_contact_days": 18},
    {"name": "Meera Nair", "company": "Cedar Health", "email": "meera@example.com", "budget": 22000, "interest_level": "High", "engagement": "High", "last_contact_days": 1},
]

def sample_leads() -> pd.DataFrame:
    """Return fictional demo leads."""
    return pd.DataFrame(SAMPLE_ROWS)


def normalize_leads(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize required fields, without mutating the caller's frame."""
    out = df.copy()
    missing = [c for c in REQUIRED_COLUMNS if c not in out.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    out = out[REQUIRED_COLUMNS].copy()
    for col in ["name", "company", "email"]:
        out[col] = out[col].fillna("").astype(str).str.strip()
    for col in ["interest_level", "engagement"]:
        out[col] = out[col].fillna("Low").astype(str).str.strip().str.title()
        out[col] = out[col].where(out[col].isin(["Low", "Medium", "High"]), "Low")
    out["budget"] = pd.to_numeric(out["budget"], errors="coerce").fillna(0).clip(lower=0)
    out["last_contact_days"] = (
        pd.to_numeric(out["last_contact_days"], errors="coerce").fillna(30).clip(lower=0)
    )
    out = out.drop_duplicates(subset=["email"], keep="first").reset_index(drop=True)
    return out


def _budget_points(budget: float) -> int:
    if budget >= 15000:
        return 30
    if budget >= 10000:
        return 24
    if budget >= 5000:
        return 17
    if budget > 0:
        return 10
    return 0


def _level_points(level: str, weights: dict[str, int]) -> int:
    return weights.get(str(level).title(), 0)


def add_lead_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Add illustrative 0-100 score, priority band and a human-readable reason."""
    out = df.copy()
    interest_weights = {"High": 30, "Medium": 18, "Low": 5}
    engagement_weights = {"High": 25, "Medium": 15, "Low": 5}

    scores, explanations = [], []
    for _, row in out.iterrows():
        budget_pts = _budget_points(float(row["budget"]))
        interest_pts = _level_points(row["interest_level"], interest_weights)
        engagement_pts = _level_points(row["engagement"], engagement_weights)
        days = float(row["last_contact_days"])
        recency_pts = 15 if days <= 3 else 12 if days <= 7 else 8 if days <= 14 else 4 if days <= 30 else 0
        score = min(100, budget_pts + interest_pts + engagement_pts + recency_pts)
        priority = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
        reasons = [
            f"budget contributes {budget_pts}/30",
            f"interest contributes {interest_pts}/30",
            f"engagement contributes {engagement_pts}/25",
            f"contact recency contributes {recency_pts}/15",
        ]
        scores.append(score)
        explanations.append(f"{priority} priority: " + "; ".join(reasons) + ".")
    out["score"] = scores
    out["priority"] = ["High" if s >= 70 else "Medium" if s >= 40 else "Low" for s in scores]
    out["score_explanation"] = explanations
    return out


def _template_follow_up(lead: dict[str, Any]) -> str:
    name = str(lead.get("name", "")).strip().split(" ")[0] or "there"
    company = str(lead.get("company", "")).strip() or "your team"
    interest = str(lead.get("interest_level", "Medium")).lower()
    return (
        f"Subject: Following up on your enquiry\n\n"
        f"Hi {name},\n\n"
        f"Thank you for your interest. I wanted to follow up and see whether "
        f"{company} would like to discuss how our solution could support your goals. "
        f"Based on your {interest} level of interest, I would be happy to arrange a short "
        f"conversation and answer any questions.\n\n"
        f"Would a brief call this week be convenient?\n\n"
        f"Best regards,\nCynbit Team"
    )


def generate_follow_up(
    lead: dict[str, Any],
    api_key: str | None = None,
    model: str = "openai/gpt-4o-mini",
) -> tuple[str, str]:
    """Try OpenRouter; safely fall back to a local template if unavailable."""
    key = (api_key or os.getenv("OPENROUTER_API_KEY", "")).strip()
    if not key:
        return _template_follow_up(lead), "local template (no API key)"

    prompt = f"""Write one concise, professional B2B follow-up email draft.
Use only the supplied facts. Do not invent product features, prices, promises, or personal details.
Do not claim that the email has been sent. Include a subject, greeting, short body, one polite call-to-action, and sign-off.
Keep it under 130 words and avoid manipulative pressure. This is a draft for human review.

Lead facts:
Name: {lead.get('name', '')}
Company: {lead.get('company', '')}
Interest level: {lead.get('interest_level', '')}
Engagement: {lead.get('engagement', '')}
Priority: {lead.get('priority', '')}
Score explanation: {lead.get('score_explanation', '')}
"""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "Cynbit LeadPilot PoC",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You draft accurate, respectful business communication for human review."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
                "max_tokens": 220,
            },
            timeout=25,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        if not content:
            raise ValueError("Empty response from model")
        return content, f"OpenRouter ({model})"
    except Exception:
        # Keep the demo usable if the key, model, network or provider is unavailable.
        return _template_follow_up(lead), "local template fallback (API unavailable)"
