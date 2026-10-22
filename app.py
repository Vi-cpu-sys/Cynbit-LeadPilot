import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from leadpilot import (
    REQUIRED_COLUMNS,
    add_lead_scores,
    generate_follow_up,
    normalize_leads,
    sample_leads,
)

load_dotenv()
st.set_page_config(page_title="Cynbit LeadPilot", page_icon="🎯", layout="wide")

st.title("🎯 Cynbit LeadPilot")
st.caption("AI-assisted lead prioritization and follow-up drafting — a proof of concept")

with st.sidebar:
    st.header("Settings")
    use_ai = st.toggle("Use OpenRouter to draft follow-ups", value=bool(os.getenv("OPENROUTER_API_KEY")))
    model = st.text_input(
        "OpenRouter model",
        value=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        help="Choose a model available to your OpenRouter account.",
    )
    st.info(
        "Lead scores are transparent rule-based estimates for demonstration, not a trained predictive model. "
        "Review all AI-generated messages before sending."
    )

st.markdown(
    "Upload a CSV of prospective leads, review the priority score and explanation, "
    "then draft a personalized follow-up. Use fictional/sample data for this demo."
)

with st.expander("Expected CSV format"):
    st.write("Required columns: `name`, `company`, `email`, `budget`, `interest_level`, `engagement`, `last_contact_days`.")
    st.write("Interest level: Low / Medium / High. Engagement: Low / Medium / High.")
    st.download_button(
        "Download sample CSV",
        data=sample_leads().to_csv(index=False).encode("utf-8"),
        file_name="sample_leads.csv",
        mime="text/csv",
    )

uploaded = st.file_uploader("Upload lead data (CSV)", type=["csv"])
if uploaded:
    try:
        raw = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Could not read this CSV: {exc}")
        st.stop()
else:
    st.info("Showing fictional sample leads. Upload your own CSV to analyze different data.")
    raw = sample_leads()

missing = [col for col in REQUIRED_COLUMNS if col not in raw.columns]
if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.stop()

try:
    leads = normalize_leads(raw)
    scored = add_lead_scores(leads)
except Exception as exc:
    st.error(f"Could not process the file: {exc}")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total leads", len(scored))
c2.metric("High priority", int((scored["priority"] == "High").sum()))
c3.metric("Medium priority", int((scored["priority"] == "Medium").sum()))
c4.metric("Low priority", int((scored["priority"] == "Low").sum()))

st.subheader("Lead overview")
priority_filter = st.multiselect(
    "Filter by priority",
    options=["High", "Medium", "Low"],
    default=["High", "Medium", "Low"],
)
view = scored[scored["priority"].isin(priority_filter)].copy()
display_cols = [
    "name", "company", "email", "budget", "interest_level", "engagement",
    "last_contact_days", "score", "priority", "score_explanation"
]
st.dataframe(view[display_cols], use_container_width=True, hide_index=True)

left, right = st.columns([1, 1])
with left:
    st.subheader("Priority distribution")
    chart_data = scored["priority"].value_counts().reindex(["High", "Medium", "Low"], fill_value=0)
    st.bar_chart(chart_data)

with right:
    st.subheader("Draft a follow-up")
    lead_options = scored.apply(lambda row: f"{row['name']} — {row['company']}", axis=1).tolist()
    selected_label = st.selectbox("Choose a lead", lead_options)
    selected_idx = lead_options.index(selected_label)
    selected = scored.iloc[selected_idx].to_dict()

    if st.button("Generate follow-up draft", type="primary"):
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        with st.spinner("Drafting message..."):
            draft, source = generate_follow_up(
                selected,
                api_key=api_key if use_ai else "",
                model=model.strip() or "openai/gpt-4o-mini",
            )
        st.session_state["draft"] = draft
        st.session_state["draft_source"] = source
        st.session_state["draft_lead"] = selected_label

    if st.session_state.get("draft_lead") == selected_label and st.session_state.get("draft"):
        st.caption(f"Draft method: {st.session_state.get('draft_source', 'template fallback')}")
        st.text_area("Editable draft (review before sending)", st.session_state["draft"], height=220)
        st.download_button(
            "Download this draft",
            data=st.session_state["draft"].encode("utf-8"),
            file_name=f"follow_up_{selected['name'].strip().replace(' ', '_')}.txt",
            mime="text/plain",
        )

st.subheader("Export")
export_cols = display_cols
csv_bytes = scored[export_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    "Download scored leads CSV",
    data=csv_bytes,
    file_name="leadpilot_scored_leads.csv",
    mime="text/csv",
)

with st.expander("How the score works"):
    st.markdown(
        """
        The score is a transparent demonstration heuristic out of 100:
        - Budget: up to 30 points
        - Interest level: up to 30 points
        - Engagement: up to 25 points
        - Recency of last contact: up to 15 points

        Priority bands: High = 70–100, Medium = 40–69, Low = 0–39.
        These thresholds and weights are illustrative and should be calibrated with real, consented CRM outcomes.
        """
    )

st.caption("Cynbit LeadPilot PoC • Fictional sample data • Human review required")
