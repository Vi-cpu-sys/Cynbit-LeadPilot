import pandas as pd
import pytest

from leadpilot import (
    REQUIRED_COLUMNS,
    add_lead_scores,
    generate_follow_up,
    normalize_leads,
    sample_leads,
)


def test_sample_leads_have_all_required_columns():
    df = sample_leads()
    assert all(column in df.columns for column in REQUIRED_COLUMNS)


def test_normalize_drops_duplicate_emails_and_handles_bad_values():
    df = sample_leads().iloc[:2].copy()
    duplicate = df.iloc[[0]].copy()
    df = pd.concat([df, duplicate], ignore_index=True)
    df.loc[1, "budget"] = "not a number"
    result = normalize_leads(df)
    assert len(result) == 2
    assert result.loc[1, "budget"] == 0


def test_missing_required_column_raises_error():
    df = sample_leads().drop(columns=["company"])
    with pytest.raises(ValueError, match="Missing required columns"):
        normalize_leads(df)


def test_scores_are_bounded_and_priorities_match_thresholds():
    scored = add_lead_scores(normalize_leads(sample_leads()))
    assert scored["score"].between(0, 100).all()
    for _, row in scored.iterrows():
        expected = "High" if row["score"] >= 70 else "Medium" if row["score"] >= 40 else "Low"
        assert row["priority"] == expected
        assert row["score_explanation"]


def test_follow_up_uses_template_without_api_key():
    lead = {
        "name": "Aarav Mehta",
        "company": "Northstar Retail",
        "interest_level": "High",
        "priority": "High",
        "score_explanation": "High priority",
    }
    draft, source = generate_follow_up(lead, api_key="")
    assert "Aarav" in draft
    assert "Subject:" in draft
    assert "template" in source
