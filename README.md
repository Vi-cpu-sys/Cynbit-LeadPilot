# Cynbit LeadPilot

**AI-assisted lead qualification and follow-up drafting — assessment proof of concept**

LeadPilot imports a CSV of prospective leads, calculates an explainable rule-based priority score, displays a Streamlit dashboard, drafts a follow-up message through OpenRouter when configured, and exports scored results.

> This is a proposed PoC for the Cynbit assessment. The sample dataset is fictional. Scoring is a transparent heuristic, not a trained predictive ML model and not a validated sales forecast. Review AI-generated messages before use.

## Features

- CSV upload and validation
- Duplicate-email removal and safe normalization of missing/invalid values
- 0–100 lead score with an explanation
- High / Medium / Low priority labels
- OpenRouter-powered follow-up drafting
- Local template fallback if no API key/network/model is available
- CSV export and downloadable message drafts

## Windows setup (PowerShell)

1. Install Python 3.11 or 3.12 and Git if not already installed.
2. Open this folder in VS Code.
3. Open **Terminal → New Terminal** and run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run this for the current terminal only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

4. Copy `.env.example` to `.env` and put your key in `OPENROUTER_API_KEY`. Do not share or commit `.env`.
5. Start the app:

```powershell
streamlit run app.py
```

Streamlit should open the app in your browser at `http://localhost:8501`.

## Test the scoring logic

```powershell
python -m pytest -q
```

## CSV schema

Required columns:

- `name`
- `company`
- `email`
- `budget` (numeric)
- `interest_level` (`Low`, `Medium`, `High`)
- `engagement` (`Low`, `Medium`, `High`)
- `last_contact_days` (number of days)

Use fictional or consented data only. Avoid uploading sensitive personal information.

## Scoring logic

- Budget: up to 30 points
- Interest: up to 30 points
- Engagement: up to 25 points
- Contact recency: up to 15 points
- High: 70–100; Medium: 40–69; Low: 0–39

The weights are illustrative. A production version should be calibrated against consented CRM data and actual outcomes, tested for bias, and reviewed by sales staff.

## OpenRouter configuration

Set `OPENROUTER_API_KEY` in `.env`. `OPENROUTER_MODEL` defaults to `openai/gpt-4o-mini`; change it to a model available to your account. If the API request fails, LeadPilot uses a local email template so the demo remains usable.

## Suggested GitHub repository structure

```text
Cynbit_LeadPilot/
├── app.py
├── leadpilot.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── data/sample_leads.csv
├── reports/AI_Opportunity_Report.md
├── reports/Technical_Approach_Report.md
└── tests/test_leadpilot.py
```

## Scope and limitations

- Scores are heuristic and must not be described as a trained ML model.
- The PoC does not send emails; it only creates drafts.
- No CRM integration or real customer data is included.
- LLM output may be incorrect; human review is required.
