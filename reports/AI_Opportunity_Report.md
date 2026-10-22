# AI Opportunity Report
## Cynbit LeadPilot: AI-Assisted Lead Qualification and Follow-up

**Prepared for:** Cynbit Technologies — AI/ML Engineer Intern Assessment  
**Project type:** Proof of concept  
**Date:** 19 October 2026

## 1. Executive summary

Cynbit LeadPilot is a proposed AI-assisted workflow for teams that receive business enquiries or manage prospective customers. It organizes lead information, assigns a transparent priority score, explains the score, and drafts a respectful follow-up message for a team member to review. The goal is to help staff decide which leads to review first and reduce the time spent writing repetitive first-draft messages.

This is a proposed opportunity based on the assessment brief and public-facing service positioning; it is not a claim that Cynbit currently has this operational problem.

## 2. Business context and opportunity

Lead management commonly involves collecting information from forms, spreadsheets, campaigns, and conversations. When information is spread across tools, staff may need to manually sort leads, identify which ones need attention, and write similar follow-up messages repeatedly.

Potential opportunities for AI/ML in this workflow include:

- **Lead prioritization:** combine declared budget, stated interest, engagement, and contact recency into a consistent first-pass score.
- **Communication assistance:** draft a short message that a staff member can edit.
- **Operational visibility:** summarize lead volumes and priority bands in one dashboard.
- **Data quality:** flag missing or inconsistent fields before the data is used.

## 3. Proposed solution

LeadPilot is a lightweight Streamlit application with five steps:

1. Import a CSV of prospective leads.
2. Validate required fields, normalize categories, and remove duplicate email entries.
3. Calculate a 0–100 score using explicit rules and show the reason for each score.
4. Draft a follow-up email using an LLM through OpenRouter, with a local template fallback.
5. Let the user review, download, and export the results.

### Illustrative score

| Factor | Maximum points | Example rule |
|---|---:|---|
| Budget | 30 | Higher declared budget receives more points |
| Stated interest | 30 | High = 30, Medium = 18, Low = 5 |
| Engagement | 25 | High = 25, Medium = 15, Low = 5 |
| Contact recency | 15 | More recent contact receives more points |
| **Total** | **100** | Sum of the four components |

Priority bands are High (70–100), Medium (40–69), and Low (0–39). These weights and thresholds are illustrative and are not statistically validated. They should be reviewed with business stakeholders and tested against real outcomes before operational use.

## 4. Expected value and success metrics

Potential benefits include less manual sorting, faster preparation of follow-up drafts, and more consistent explanations for prioritization. These are hypotheses to test, not measured results.

A pilot could track:

- Median time spent reviewing and preparing a lead follow-up.
- Percentage of generated drafts accepted with minor edits.
- Percentage of leads with complete and valid fields.
- Sales-team agreement with the priority bands.
- Conversion rate by priority band, measured over a suitable period.
- Error rate and user-reported issues.

Compare these metrics with a baseline before claiming business impact.

## 5. Alternatives considered

- **Rules-only scoring:** transparent and easy to explain, but does not learn from outcomes. Chosen for the initial PoC because no labeled historical CRM data is provided.
- **Supervised ML ranking:** could learn patterns from historical conversions, but requires enough representative, lawful, well-labeled data and validation.
- **LLM-only scoring:** flexible but less consistent and harder to audit. Not selected for numeric lead scoring.
- **LLM-assisted message drafting:** suitable for language generation when prompts restrict unsupported claims and a human reviews the result.

## 6. Risks and safeguards

- **Incorrect prioritization:** expose the score breakdown and let staff override it.
- **LLM hallucination:** instruct the model to use only supplied facts; require human review.
- **Privacy:** use fictional data for the demo, restrict access, and minimize personal data sent to an external API.
- **Bias or unfair treatment:** do not use protected or sensitive traits; evaluate outcomes before production use.
- **Over-reliance:** label the score as an estimate, not a prediction of a person's worth or guaranteed conversion.
- **API failure or cost:** use a local template fallback and monitor usage.
- **Security:** keep API keys in environment variables and never commit secrets.

## 7. Recommended next steps

1. Interview the team to understand its current lead workflow and CRM tools.
2. Agree on the definition of a qualified lead and relevant business metrics.
3. Run the PoC with synthetic data and obtain feedback from potential users.
4. If approved, evaluate a small, consented and access-controlled dataset.
5. Compare the heuristic with actual outcomes and establish a baseline.
6. Add CRM integration only after security, privacy, and workflow requirements are approved.

## 8. Conclusion

LeadPilot demonstrates one practical way AI-assisted prioritization and text generation could fit a lead-management workflow. Its main strength is a small, explainable end-to-end demo with a human review step. The next decision should be based on stakeholder feedback and measured pilot results, not assumed impact.
