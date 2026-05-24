# NorthPoint Financial — Marketing Analytics System

I signed up for a digital bank last month. Got the welcome email. Set up my account. Then never really used it.

I wonder how many people do exactly the same thing and what that costs the company.

Turns out it costs a lot. And the data to understand exactly why has always been there. Nobody just built the system to look at it properly.

So I did.

---

## What this is

A full marketing analytics system for a fictional Canadian digital bank called NorthPoint Financial. 18 months of customer acquisition and behaviour data across four channels. Five analytical layers. A deployed Streamlit app that works the way an internal marketing analytics tool would actually work.

This is not a tutorial project. It is the work a marketing analyst at a company like Amex, Scotia, or a Canadian fintech does on a Monday morning when their manager asks why retention dropped last quarter.

---

## Live app

[Launch the NorthPoint Marketing Analytics System](your-streamlit-link-here](https://northpoint-marketing-analytics-2d8lsfjebvpvazprsttmvu.streamlit.app/))

---

## The core finding

Paid Social is the highest volume acquisition channel. It is also the only channel where the company spends more to acquire a customer than it earns back from them. The LTV-to-CAC ratio for Paid Social is 0.88. Anything below 1.0 means the channel is a net cost centre.

Referral customers cost more to acquire than Paid Social customers. But they stay 3.6 times longer, generate more monthly revenue, and produce a 2.5x LTV-to-CAC ratio. The cheapest channel to acquire a customer is almost never the best one.

| Channel | Avg CAC | 90-Day Retention | LTV to CAC | Sustainable? |
|---------|---------|-----------------|------------|--------------|
| Paid Social | $85.69 | 13.6% | 0.88x | No |
| Organic Search | $35.50 | 31.2% | 3.3x | Yes |
| Referral | $55.18 | 48.9% | 2.5x | Yes |
| Email Campaign | $17.94 | 10.8% | 2.84x | Yes |

---

## What the five tabs cover

The acquisition funnel tab shows the full customer journey from signup to activation to 90-day retention for each channel side by side. An interactive scatter plot shows the relationship between CAC and 90-day retention so the tradeoffs are immediately visible.

The cohort retention tab is a colour-coded heatmap showing the percentage of each monthly acquisition cohort still active at 30, 60, 90, and 180 days. Darker green is better retention. Pale rows are the cohorts that churned fastest.

The CLV and CAC model tab shows estimated lifetime value against actual and maximum justified CAC for each customer segment. Every segment is currently being over-acquired relative to its lifetime value.

The campaign performance tab shows three email campaigns with A/B test results. Each test includes a chi-square significance test with a plain English interpretation of whether the result is statistically real or could be due to chance.

The executive summary tab is a one-page brief with the three key findings and two recommended actions written the way you would present them to a VP of Marketing.

---

## Files in this repo

| File | What it is |
|------|-----------|
| app.py | The Streamlit analytics app — 5 tabs, interactive filters, real-time charts |
| customer-data.csv | 2,400 synthetic customer records with acquisition channel, activation, retention milestones, and revenue |
| campaign-data.csv | 3 email campaigns with A/B test results across open rate, click rate, conversion, and revenue |
| funnel-analysis.csv | Full funnel metrics by channel including LTV-to-CAC ratio |
| cohort-retention.csv | 18 monthly cohorts with retention rates at Day 30, 60, 90, and 180 |
| clv-model.csv | Customer lifetime value and CAC model by segment |
| generate-data.py | The Python script that built the synthetic dataset |
| requirements.txt | Package dependencies for Streamlit Cloud |

---

## How to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Skills this project demonstrates

Customer acquisition funnel analysis. Cohort retention modelling. Customer lifetime value and CAC calculation. A/B test design and chi-square significance testing. Customer segmentation. Marketing analytics dashboard design. Python with pandas, plotly, scipy, and streamlit. Findings brief writing in a format a marketing leadership team would actually use. Financial services and fintech product context.

---

## About this project

This is part of a portfolio series built while job searching in Canada after graduating from the University of Waterloo.

Prepared by Simran Saran. Targeting roles in marketing analytics, business analysis, and growth at financial services and fintech companies across Canada.

All customer data is synthetic. NorthPoint Financial is fictional. Channel characteristics and retention benchmarks are modelled on publicly available fintech industry data.
