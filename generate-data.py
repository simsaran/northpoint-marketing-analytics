import csv
import random
from datetime import date, timedelta
import math

random.seed(2024)

# NorthPoint Financial -- fictional Canadian digital bank
# 18 months of customer acquisition and behaviour data
# January 2024 to June 2025

CHANNELS = ["Paid Social", "Organic Search", "Referral", "Email Campaign"]

# Channel characteristics -- realistic for Canadian fintech
CHANNEL_PROFILES = {
    "Paid Social": {
        "weight": 40,
        "avg_cac": 85,
        "cac_variance": 20,
        "activation_rate": 0.58,
        "day30_retention": 0.42,
        "day60_retention": 0.31,
        "day90_retention": 0.24,
        "day180_retention": 0.16,
        "avg_monthly_revenue": 12.50,
        "revenue_variance": 8,
    },
    "Organic Search": {
        "weight": 25,
        "avg_cac": 35,
        "cac_variance": 10,
        "activation_rate": 0.72,
        "day30_retention": 0.61,
        "day60_retention": 0.49,
        "day90_retention": 0.41,
        "day180_retention": 0.32,
        "avg_monthly_revenue": 18.00,
        "revenue_variance": 9,
    },
    "Referral": {
        "weight": 20,
        "avg_cac": 55,
        "cac_variance": 12,
        "activation_rate": 0.81,
        "day30_retention": 0.74,
        "day60_retention": 0.63,
        "day90_retention": 0.57,
        "day180_retention": 0.46,
        "avg_monthly_revenue": 22.50,
        "revenue_variance": 10,
    },
    "Email Campaign": {
        "weight": 15,
        "avg_cac": 18,
        "cac_variance": 6,
        "activation_rate": 0.49,
        "day30_retention": 0.38,
        "day60_retention": 0.27,
        "day90_retention": 0.19,
        "day180_retention": 0.11,
        "avg_monthly_revenue": 9.00,
        "revenue_variance": 5,
    },
}

SEGMENTS = ["High Value", "Medium Value", "Low Value", "Churned"]

def assign_segment(monthly_rev, is_active_90):
    if not is_active_90:
        return "Churned"
    if monthly_rev >= 25:
        return "High Value"
    elif monthly_rev >= 12:
        return "Medium Value"
    else:
        return "Low Value"

start_date = date(2024, 1, 1)
end_date = date(2025, 6, 30)
total_days = (end_date - start_date).days

customers = []
customer_id = 1

# Generate 2400 customers across 18 months
for _ in range(2400):
    channel = random.choices(
        CHANNELS,
        weights=[CHANNEL_PROFILES[c]["weight"] for c in CHANNELS]
    )[0]
    profile = CHANNEL_PROFILES[channel]

    day_offset = random.randint(0, total_days)
    signup_date = start_date + timedelta(days=day_offset)
    month_str = signup_date.strftime("%Y-%m")

    cac = max(5, round(random.gauss(profile["avg_cac"], profile["cac_variance"]), 2))
    activated = random.random() < profile["activation_rate"]

    if activated:
        activation_date = signup_date + timedelta(days=random.randint(0, 3))
    else:
        activation_date = None

    active_30 = activated and random.random() < profile["day30_retention"]
    active_60 = active_30 and random.random() < (profile["day60_retention"] / profile["day30_retention"])
    active_90 = active_60 and random.random() < (profile["day90_retention"] / profile["day60_retention"])
    active_180 = active_90 and random.random() < (profile["day180_retention"] / profile["day90_retention"])

    monthly_rev = 0
    if activated:
        monthly_rev = max(0, round(random.gauss(
            profile["avg_monthly_revenue"],
            profile["revenue_variance"]
        ), 2))
    if not active_90:
        monthly_rev = max(0, monthly_rev * 0.3)

    segment = assign_segment(monthly_rev, active_90)

    days_active = 0
    if active_180:
        days_active = random.randint(120, 180)
    elif active_90:
        days_active = random.randint(60, 120)
    elif active_60:
        days_active = random.randint(30, 60)
    elif active_30:
        days_active = random.randint(10, 30)
    elif activated:
        days_active = random.randint(1, 10)

    customers.append({
        "Customer ID": f"NP{str(customer_id).zfill(5)}",
        "Signup Date": signup_date.strftime("%Y-%m-%d"),
        "Acquisition Month": month_str,
        "Channel": channel,
        "CAC CAD": cac,
        "Activated": "Yes" if activated else "No",
        "Activation Date": activation_date.strftime("%Y-%m-%d") if activation_date else "",
        "Active Day 30": "Yes" if active_30 else "No",
        "Active Day 60": "Yes" if active_60 else "No",
        "Active Day 90": "Yes" if active_90 else "No",
        "Active Day 180": "Yes" if active_180 else "No",
        "Days Active": days_active,
        "Monthly Revenue CAD": monthly_rev,
        "Customer Segment": segment,
    })
    customer_id += 1

customers.sort(key=lambda x: x["Signup Date"])

with open('/home/claude/northpoint-marketing/customer-data.csv','w',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=customers[0].keys())
    writer.writeheader()
    writer.writerows(customers)

print(f"Customer dataset: {len(customers)} customers")

# Verify channel distribution
from collections import Counter
channel_counts = Counter(c["Channel"] for c in customers)
for ch, count in channel_counts.most_common():
    activated = sum(1 for c in customers if c["Channel"]==ch and c["Activated"]=="Yes")
    active90 = sum(1 for c in customers if c["Channel"]==ch and c["Active Day 90"]=="Yes")
    avg_cac = sum(float(c["CAC CAD"]) for c in customers if c["Channel"]==ch) / count
    print(f"  {ch}: {count} customers, {round(activated/count*100,1)}% activated, {round(active90/count*100,1)}% active at 90d, avg CAC ${round(avg_cac,2)}")

# ── CAMPAIGN DATA ─────────────────────────────────────────────────────────────
campaigns = []

campaign_specs = [
    {
        "Campaign ID": "CAM-001",
        "Campaign Name": "Q1 Onboarding Reactivation",
        "Type": "Email",
        "Target Segment": "Low Value",
        "Send Date": "2024-02-15",
        "Subject Line A": "Your NorthPoint account is waiting for you",
        "Subject Line B": "You have $25 ready to unlock in your account",
        "Audience Size A": 600,
        "Audience Size B": 600,
        "Open Rate A %": 18.4,
        "Open Rate B %": 31.2,
        "Click Rate A %": 4.2,
        "Click Rate B %": 9.8,
        "Conversion Rate A %": 1.8,
        "Conversion Rate B %": 4.1,
        "Revenue Attributed A CAD": 648,
        "Revenue Attributed B CAD": 1476,
        "Campaign Cost CAD": 2400,
    },
    {
        "Campaign ID": "CAM-002",
        "Campaign Name": "Spring Rewards Launch",
        "Type": "Email",
        "Target Segment": "Medium Value",
        "Send Date": "2024-04-01",
        "Subject Line A": "New rewards waiting for you this spring",
        "Subject Line B": "Double points this April — here is how",
        "Audience Size A": 800,
        "Audience Size B": 800,
        "Open Rate A %": 22.1,
        "Open Rate B %": 34.8,
        "Click Rate A %": 6.4,
        "Click Rate B %": 12.3,
        "Conversion Rate A %": 2.9,
        "Conversion Rate B %": 5.7,
        "Revenue Attributed A CAD": 1392,
        "Revenue Attributed B CAD": 2736,
        "Campaign Cost CAD": 3200,
    },
    {
        "Campaign ID": "CAM-003",
        "Campaign Name": "High Value Retention Push",
        "Type": "Email",
        "Target Segment": "High Value",
        "Send Date": "2024-07-10",
        "Subject Line A": "Thank you for being a NorthPoint member",
        "Subject Line B": "A personal offer for our most valued members",
        "Audience Size A": 300,
        "Audience Size B": 300,
        "Open Rate A %": 38.2,
        "Open Rate B %": 52.6,
        "Click Rate A %": 14.1,
        "Click Rate B %": 22.8,
        "Conversion Rate A %": 7.2,
        "Conversion Rate B %": 11.4,
        "Revenue Attributed A CAD": 1296,
        "Revenue Attributed B CAD": 2052,
        "Campaign Cost CAD": 1800,
    },
]

with open('/home/claude/northpoint-marketing/campaign-data.csv','w',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=campaigns[0].keys() if campaigns else campaign_specs[0].keys())
    writer.writeheader()
    writer.writerows(campaign_specs)

print(f"\nCampaign dataset: {len(campaign_specs)} campaigns written")

# ── FUNNEL DATA ───────────────────────────────────────────────────────────────
funnel_rows = []
for ch in CHANNELS:
    ch_customers = [c for c in customers if c["Channel"]==ch]
    total = len(ch_customers)
    visited = total
    signed_up = total
    activated = sum(1 for c in ch_customers if c["Activated"]=="Yes")
    active30 = sum(1 for c in ch_customers if c["Active Day 30"]=="Yes")
    active90 = sum(1 for c in ch_customers if c["Active Day 90"]=="Yes")
    avg_cac = sum(float(c["CAC CAD"]) for c in ch_customers) / total
    avg_rev = sum(float(c["Monthly Revenue CAD"]) for c in ch_customers if c["Active Day 90"]=="Yes")
    avg_rev_per = avg_rev / active90 if active90 > 0 else 0

    funnel_rows.append({
        "Channel": ch,
        "Total Signups": total,
        "Activated": activated,
        "Activation Rate %": round(activated/total*100,1),
        "Active at Day 30": active30,
        "Day 30 Retention %": round(active30/total*100,1),
        "Active at Day 90": active90,
        "Day 90 Retention %": round(active90/total*100,1),
        "Avg CAC CAD": round(avg_cac,2),
        "Avg Monthly Revenue (Active 90d) CAD": round(avg_rev_per,2),
        "Estimated 6M LTV CAD": round(avg_rev_per*6,2),
        "LTV to CAC Ratio": round((avg_rev_per*6)/avg_cac,2),
        "CAC Justified by LTV?": "Yes" if (avg_rev_per*6) > avg_cac else "No",
    })

with open('/home/claude/northpoint-marketing/funnel-analysis.csv','w',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=funnel_rows[0].keys())
    writer.writeheader()
    writer.writerows(funnel_rows)

print("\nFunnel analysis:")
for r in funnel_rows:
    print(f"  {r['Channel']}: {r['Day 90 Retention %']}% at 90d, LTV/CAC = {r['LTV to CAC Ratio']}, CAC justified = {r['CAC Justified by LTV?']}")

# ── COHORT TABLE ──────────────────────────────────────────────────────────────
months = sorted(set(c["Acquisition Month"] for c in customers))
cohort_rows = []
for month in months:
    cohort = [c for c in customers if c["Acquisition Month"]==month]
    total = len(cohort)
    if total == 0:
        continue
    activated = sum(1 for c in cohort if c["Activated"]=="Yes")
    active30 = sum(1 for c in cohort if c["Active Day 30"]=="Yes")
    active60 = sum(1 for c in cohort if c["Active Day 60"]=="Yes")
    active90 = sum(1 for c in cohort if c["Active Day 90"]=="Yes")
    active180 = sum(1 for c in cohort if c["Active Day 180"]=="Yes")

    cohort_rows.append({
        "Cohort Month": month,
        "Total Customers": total,
        "Activation Rate %": round(activated/total*100,1),
        "Day 30 Retention %": round(active30/total*100,1),
        "Day 60 Retention %": round(active60/total*100,1),
        "Day 90 Retention %": round(active90/total*100,1),
        "Day 180 Retention %": round(active180/total*100,1),
        "Avg CAC CAD": round(sum(float(c["CAC CAD"]) for c in cohort)/total,2),
    })

with open('/home/claude/northpoint-marketing/cohort-retention.csv','w',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=cohort_rows[0].keys())
    writer.writeheader()
    writer.writerows(cohort_rows)

print(f"\nCohort table: {len(cohort_rows)} monthly cohorts written")

# ── CLV AND CAC MODEL ─────────────────────────────────────────────────────────
clv_rows = []
for seg in ["High Value", "Medium Value", "Low Value"]:
    seg_customers = [c for c in customers if c["Customer Segment"]==seg]
    if not seg_customers:
        continue
    count = len(seg_customers)
    avg_monthly_rev = sum(float(c["Monthly Revenue CAD"]) for c in seg_customers) / count
    avg_days_active = sum(int(c["Days Active"]) for c in seg_customers) / count
    avg_months_active = avg_days_active / 30
    estimated_ltv = round(avg_monthly_rev * avg_months_active, 2)
    max_cac = round(estimated_ltv * 0.33, 2)
    actual_cac_all = sum(float(c["CAC CAD"]) for c in seg_customers) / count

    clv_rows.append({
        "Segment": seg,
        "Customer Count": count,
        "Avg Monthly Revenue CAD": round(avg_monthly_rev,2),
        "Avg Active Months": round(avg_months_active,1),
        "Estimated LTV CAD": estimated_ltv,
        "Max Justified CAC CAD": max_cac,
        "Actual Avg CAC CAD": round(actual_cac_all,2),
        "CAC vs Max Justified": "Over" if actual_cac_all > max_cac else "Under",
        "Profit per Customer CAD": round(estimated_ltv - actual_cac_all,2),
    })

with open('/home/claude/northpoint-marketing/clv-model.csv','w',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=clv_rows[0].keys())
    writer.writeheader()
    writer.writerows(clv_rows)

print("\nCLV model:")
for r in clv_rows:
    print(f"  {r['Segment']}: LTV ${r['Estimated LTV CAD']}, max CAC ${r['Max Justified CAC CAD']}, actual CAC ${r['Actual Avg CAC CAD']} ({r['CAC vs Max Justified']})")
print("\nAll files written successfully.")
