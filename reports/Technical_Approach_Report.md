# Technical Approach Report
## Cynbit LeadPilot

**Prepared for:** Cynbit Technologies — AI/ML Engineer Intern Assessment  
**Date:** 19 October 2026

## 1. Objective

Build a working proof of concept that accepts lead data, validates it, calculates an explainable priority score, drafts a follow-up message, and exports the results.

## 2. Architecture

```text
CSV upload
   |
   v
Pandas validation and normalization
   |
   v
Rule-based scoring engine --------------------+
   |                                          |
   v                                          v
Priority + score explanation             Streamlit dashboard
   |                                          |
   +------------------+-----------------------+
                      |
                      v
            User selects a lead
                      |
                      v
       OpenRouter chat-completions API
                      |
             success / failure
                /          \
               v            v
         LLM draft      Local template
                \          /
                 v        v
              Human review
                    |
                    v
           Download draft / CSV
```

## 3. Technology choices

- **Python:** core logic and integration.
- **Pandas:** CSV parsing, normalization, duplicate handling, and export.
- **Streamlit:** quick interactive dashboard suitable for a compact PoC.
- **OpenRouter API:** access to a configured chat model for follow-up drafting.
- **Requests:** HTTP integration with timeout and error fallback.
- **python-dotenv:** load secrets from a local `.env` file.
- **pytest:** unit tests for scoring and normalization.

## 4. Data pipeline

Input requires `name`, `company`, `email`, `budget`, `interest_level`, `engagement`, and `last_contact_days`.

1. Check for required columns and stop with a clear error if any are absent.
2. Trim text fields and replace missing names/company/email with empty strings.
3. Normalize interest and engagement categories; unknown values become Low for this demonstration.
4. Convert budget and days-since-contact to numeric values; invalid values receive safe defaults and negative values are clipped.
5. Remove duplicate email rows, keeping the first occurrence.
6. Score each lead and generate an explanation for the displayed score.
7. Display results and export CSV.

For production, invalid data should be flagged for correction rather than silently treated as a valid low-interest lead. This simplification is acceptable only for demonstrating the flow.

## 5. Scoring model

This PoC uses a deterministic rule-based score rather than a trained ML model because no labeled historical conversion dataset is supplied.

- Budget: 0–30 points, based on illustrative thresholds.
- Interest: Low 5, Medium 18, High 30.
- Engagement: Low 5, Medium 15, High 25.
- Contact recency: 0–15 points based on days since last contact.
- Total: sum of components, capped at 100.
- Bands: High ≥ 70; Medium ≥ 40; otherwise Low.

The UI exposes component-level reasoning. We should not describe this as predictive accuracy or claim that the bands improve conversion without evaluation.

## 6. LLM prompt design

The prompt requests a concise B2B email draft with a subject, greeting, short body, one polite call to action, and sign-off. It instructs the model to:

- use only supplied facts;
- avoid invented features, prices, promises, and personal details;
- avoid manipulative pressure;
- keep the message under 130 words;
- never claim that the message has been sent; and
- leave the result for human review.

The selected model is configurable using `OPENROUTER_MODEL`. The API key is loaded from `OPENROUTER_API_KEY`, not source code. If the request fails, a local template is returned.

## 7. Error handling and security

- Missing columns are reported to the user.
- CSV parsing and processing errors are caught and displayed.
- API calls use a timeout and fall back to a template on failure.
- Secrets are excluded through `.gitignore`.
- Sample data is fictional.
- The app creates drafts only; it does not send messages.
- Avoid uploading sensitive personal information. For production, assess data retention, consent, access control, and whether sending lead details to an external model is permitted.

## 8. Test plan

- Required-column validation rejects incomplete CSVs.
- Duplicate emails are removed.
- Invalid numeric values are normalized safely.
- Scores remain between 0 and 100.
- Priority bands follow the documented thresholds.
- Follow-up drafting works without an API key using the local template.
- The app can export scored leads to CSV.

Run: `python -m pytest -q`

## 9. Execution plan

1. Install dependencies in an isolated Python virtual environment.
2. Run unit tests.
3. Launch Streamlit locally.
4. Test the sample dataset and a custom CSV.
5. Test with a valid OpenRouter key and configured model.
6. Confirm fallback behavior with the key removed or network disabled.
7. Review output for accuracy, readability, and privacy.
8. Commit code and reports to GitHub; optionally deploy the app using Streamlit Community Cloud after verifying that secrets are configured securely.

## 10. Limitations and future work

The current score is heuristic, not a trained model. No real CRM connection, email sending, user authentication, or persistent database is included. Future work could include CRM integration, configurable scoring weights, audit logs, human override tracking, evaluation against labeled outcomes, and a validated supervised ranking model if sufficient appropriate data becomes available.
