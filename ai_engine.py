import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def build_case_context(case):
    """
    Convert the selected claim into grounded text for the AI.
    """

    reasons = case["risk_reasons"]

    if reasons:
        reason_text = "\n".join(
            [f"- {reason}" for reason in reasons]
        )
    else:
        reason_text = "- No major risk indicators were triggered."

    context = f"""
CASE INFORMATION

Case ID: {case['case_id']}
Claim Number: {case['claim_number']}
Claim Date: {case['claim_date']}
Care Type: {case['care_type']}
Claim Amount: ${case['claim_amount_usd']:,.0f}
State: {case['state']}

TRIAGE ASSESSMENT

Risk Score: {case['risk_score']}/100
Risk Level: {case['risk_level']}

DETECTED RISK INDICATORS

{reason_text}

RAW CASE SIGNALS

Duplicate service billed: {case['duplicate_service_billed']}
Weekly visit frequency: {case['weekly_visit_frequency']}
Member-provider distance: {case['member_provider_distance_miles']} miles
Prior claims last 12 months: {case['prior_claims_last_12mo']}
Shared contact with provider: {case['shared_contact_with_provider']}
Weekend billing ratio: {case['weekend_billing_ratio']:.0%}
Amount vs peer average: {case['amount_vs_peer_avg_pct']}%
Round-dollar billing ratio: {case['round_dollar_billing_ratio']:.0%}
Recent policy change: {case['recent_policy_change_flag']}
Service overlap with another provider: {case['service_overlap_other_provider']}

Recommended triage action:
{case['recommended_action']}
"""

    return context


def generate_case_summary(case):
    """
    Generate a grounded AI assessment for the selected case.
    """

    case_context = build_case_context(case)

    prompt = f"""
You are a Junior AI Investigator assisting a human insurance
fraud investigator.

Your task is to review ONLY the supplied synthetic case data.

IMPORTANT RULES:

1. Never state that fraud definitely occurred.
2. Never invent facts that are not present in the case data.
3. Clearly distinguish indicators from conclusions.
4. If information is missing, say it is not available.
5. The human investigator makes the final decision.
6. Keep your response concise and useful.

CASE DATA:

{case_context}

Produce this exact structure:

ASSESSMENT:
Write 2-3 sentences summarizing why this case should receive
its current priority.

STRONGEST EVIDENCE:
List the 3 most important indicators.

COUNTER-EVIDENCE / UNCERTAINTY:
Identify evidence that reduces suspicion or explain what
important information is missing.

RECOMMENDED NEXT STEP:
Give one concrete action for the investigator.
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    return response.output_text


def ask_case_question(case, question):
    """
    Answer investigator questions using only selected case data.
    """

    case_context = build_case_context(case)

    prompt = f"""
You are a Junior AI Investigator helping an insurance fraud
investigator review a synthetic claim.

Use ONLY the supplied case information.

Do not invent:
- provider history
- customer history
- medical records
- criminal records
- policy details
- external facts

If the question cannot be answered from the supplied case
information, explicitly say:

"The available case data does not provide that information."

Never state that fraud definitely occurred.

CASE DATA:

{case_context}

INVESTIGATOR QUESTION:

{question}

Give a concise, evidence-based answer.
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    return response.output_text