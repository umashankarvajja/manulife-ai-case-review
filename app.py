import streamlit as st
import pandas as pd

from risk_engine import calculate_risk
from ai_engine import generate_case_summary, ask_case_question


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Junior AI Investigator",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Junior AI Investigator")
st.subheader("AI-First Case Review for Fraud Investigators")

st.caption(
    "AI-assisted triage for synthetic insurance referrals. "
    "The AI supports investigator review and does not determine whether fraud occurred."
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("data/sample_cases_synthetic.csv")


# ============================================================
# CALCULATE RISK FOR EVERY CASE
# ============================================================

risk_scores = []
risk_levels = []
recommended_actions = []
risk_reasons = []

for _, case in df.iterrows():

    score, level, reasons, action = calculate_risk(case)

    risk_scores.append(score)
    risk_levels.append(level)
    recommended_actions.append(action)
    risk_reasons.append(reasons)


df["risk_score"] = risk_scores
df["risk_level"] = risk_levels
df["recommended_action"] = recommended_actions
df["risk_reasons"] = risk_reasons


# ============================================================
# DASHBOARD METRICS
# ============================================================

total_cases = len(df)

high_cases = len(
    df[df["risk_level"] == "HIGH"]
)

medium_cases = len(
    df[df["risk_level"] == "MEDIUM"]
)

low_cases = len(
    df[df["risk_level"] == "LOW"]
)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Cases",
    total_cases
)

col2.metric(
    "🔴 High Risk",
    high_cases
)

col3.metric(
    "🟡 Medium Risk",
    medium_cases
)

col4.metric(
    "🟢 Low Risk",
    low_cases
)


st.divider()


# ============================================================
# INVESTIGATION QUEUE
# ============================================================

st.header("Investigation Queue")


risk_filter = st.selectbox(
    "Filter by Risk Level",
    [
        "ALL",
        "HIGH",
        "MEDIUM",
        "LOW"
    ]
)


if risk_filter != "ALL":

    filtered_df = df[
        df["risk_level"] == risk_filter
    ].copy()

else:

    filtered_df = df.copy()


# Sort HIGH → MEDIUM → LOW

risk_order = {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3
}

filtered_df["risk_order"] = (
    filtered_df["risk_level"]
    .map(risk_order)
)

filtered_df = filtered_df.sort_values(
    by=[
        "risk_order",
        "risk_score"
    ],
    ascending=[
        True,
        False
    ]
)


# ============================================================
# CASE SELECTION
# ============================================================

case_options = []

for _, row in filtered_df.iterrows():

    label = (
        f"{row['case_id']} | "
        f"{row['claim_number']} | "
        f"${row['claim_amount_usd']:,.0f} | "
        f"{row['risk_level']}"
    )

    case_options.append(label)


selected_label = st.selectbox(
    "Choose a case to review",
    case_options
)


selected_case_id = (
    selected_label
    .split(" | ")[0]
)


selected_case = (
    df[
        df["case_id"] == selected_case_id
    ]
    .iloc[0]
)


# ============================================================
# CROSS-CASE INTELLIGENCE
# ============================================================

# Find other records in the queue with the same claim number

related_cases = df[
    (df["claim_number"] == selected_case["claim_number"]) &
    (df["case_id"] != selected_case["case_id"])
]


# ============================================================
# CASE REVIEW
# ============================================================

st.divider()

st.header(
    f"Case Review: {selected_case['case_id']}"
)


# ============================================================
# CROSS-CASE ALERT
# ============================================================

if not related_cases.empty:

    st.warning(
        "⚠️ Cross-Case Signal Detected"
    )

    st.markdown(
        f"Claim number **{selected_case['claim_number']}** "
        f"also appears in another referral in the current investigation queue."
    )

    for _, related in related_cases.iterrows():

        st.markdown(
            f"""
**Related Case:** {related['case_id']}  
**Care Type:** {related['care_type']}  
**Claim Amount:** ${related['claim_amount_usd']:,.0f}  
**State:** {related['state']}  
**Claim Date:** {related['claim_date']}
"""
        )

    st.caption(
        "Recommended: Review the related referral before making "
        "a final disposition. A repeated claim number is a queue-level "
        "relationship signal, not proof of fraud."
    )


# ============================================================
# RISK BANNER
# ============================================================

if selected_case["risk_level"] == "HIGH":

    st.error(
        f"🔴 HIGH RISK — "
        f"Score: {selected_case['risk_score']}/100"
    )

elif selected_case["risk_level"] == "MEDIUM":

    st.warning(
        f"🟡 MEDIUM RISK — "
        f"Score: {selected_case['risk_score']}/100"
    )

else:

    st.success(
        f"🟢 LOW RISK — "
        f"Score: {selected_case['risk_score']}/100"
    )


# ============================================================
# CLAIM INFORMATION
# ============================================================

st.subheader("Claim Information")


info1, info2, info3 = st.columns(3)


with info1:

    st.markdown("**Claim Number**")
    st.write(selected_case["claim_number"])

    st.markdown("**Case ID**")
    st.write(selected_case["case_id"])


with info2:

    st.markdown("**Claim Amount**")
    st.write(
        f"${selected_case['claim_amount_usd']:,.0f}"
    )

    st.markdown("**Care Type**")
    st.write(selected_case["care_type"])


with info3:

    st.markdown("**State**")
    st.write(selected_case["state"])

    st.markdown("**Claim Date**")
    st.write(selected_case["claim_date"])


# ============================================================
# WHY THIS CASE WAS PRIORITIZED
# ============================================================

st.subheader(
    "Why This Case Was Prioritized"
)


reasons = selected_case["risk_reasons"]


if reasons:

    for reason in reasons:

        st.write(
            f"⚠️ {reason}"
        )

else:

    st.success(
        "No major fraud-style indicators were triggered."
    )


# ============================================================
# RECOMMENDED NEXT ACTION
# ============================================================

st.subheader(
    "Recommended Next Action"
)

st.info(
    selected_case[
        "recommended_action"
    ]
)


# ============================================================
# AI CASE ASSESSMENT
# ============================================================

st.divider()

st.header(
    "🤖 AI Case Assessment"
)

st.caption(
    "The AI is grounded only in the supplied synthetic case data. "
    "It does not make a final fraud determination."
)


summary_key = (
    f"ai_summary_{selected_case['case_id']}"
)


if st.button(
    "Generate AI Assessment",
    type="primary"
):

    with st.spinner(
        "Junior AI Investigator is reviewing the evidence..."
    ):

        try:

            ai_summary = generate_case_summary(
                selected_case
            )

            st.session_state[
                summary_key
            ] = ai_summary

        except Exception as e:

            st.error(
                "The AI assessment could not be generated."
            )

            st.caption(
                f"Technical details: {e}"
            )


if summary_key in st.session_state:

    st.markdown(
        st.session_state[
            summary_key
        ]
    )


# ============================================================
# VIEW ALL RAW SIGNALS
# ============================================================

st.divider()


with st.expander(
    "🔎 View All Case Signals"
):

    signal1, signal2 = st.columns(2)


    with signal1:

        st.markdown(
            "### Billing & Service Signals"
        )

        st.write(
            "**Duplicate Service Billed:**",
            "Yes"
            if selected_case[
                "duplicate_service_billed"
            ] == 1
            else "No"
        )

        st.write(
            "**Weekly Visit Frequency:**",
            selected_case[
                "weekly_visit_frequency"
            ]
        )

        st.write(
            "**Weekend Billing Ratio:**",
            f"{selected_case['weekend_billing_ratio']:.0%}"
        )

        st.write(
            "**Round-Dollar Billing Ratio:**",
            f"{selected_case['round_dollar_billing_ratio']:.0%}"
        )

        st.write(
            "**Service Overlap With Other Provider:**",
            "Yes"
            if selected_case[
                "service_overlap_other_provider"
            ] == 1
            else "No"
        )


    with signal2:

        st.markdown(
            "### Member & Claim Signals"
        )

        st.write(
            "**Member-Provider Distance:**",
            f"{selected_case['member_provider_distance_miles']} miles"
        )

        st.write(
            "**Prior Claims Last 12 Months:**",
            selected_case[
                "prior_claims_last_12mo"
            ]
        )

        st.write(
            "**Shared Contact With Provider:**",
            "Yes"
            if selected_case[
                "shared_contact_with_provider"
            ] == 1
            else "No"
        )

        st.write(
            "**Amount vs Peer Average:**",
            f"{selected_case['amount_vs_peer_avg_pct']}%"
        )

        st.write(
            "**Recent Policy Change:**",
            "Yes"
            if selected_case[
                "recent_policy_change_flag"
            ] == 1
            else "No"
        )


# ============================================================
# HUMAN-IN-THE-LOOP REVIEW
# ============================================================

st.divider()

st.header(
    "👤 Investigator Decision"
)

st.caption(
    "The investigator remains responsible for the final disposition."
)


decision = st.radio(
    "What do you want to do with this AI assessment?",
    [
        "Needs More Investigation",
        "Accept AI Assessment",
        "Reject AI Assessment"
    ],
    key=f"decision_{selected_case['case_id']}"
)


notes = st.text_area(
    "Investigator Notes",
    placeholder=(
        "Add observations, evidence to verify, "
        "or reasons for accepting/rejecting the AI assessment..."
    ),
    key=f"notes_{selected_case['case_id']}"
)


if st.button(
    "Save Review"
):

    st.session_state[
        f"saved_decision_{selected_case['case_id']}"
    ] = decision

    st.session_state[
        f"saved_notes_{selected_case['case_id']}"
    ] = notes

    st.success(
        f"Review saved for "
        f"{selected_case['case_id']} — "
        f"Decision: {decision}"
    )


# ============================================================
# ASK THE JUNIOR AI INVESTIGATOR
# ============================================================

st.divider()

st.header(
    "💬 Ask the Junior AI Investigator"
)

st.caption(
    "Ask a question about the selected case. "
    "The AI must answer only from the available case evidence."
)


question = st.text_input(
    "Ask a question",
    placeholder=(
        "Example: What should I investigate first?"
    ),
    key=f"question_{selected_case['case_id']}"
)


if st.button(
    "Ask AI"
):

    if question.strip():

        with st.spinner(
            "Reviewing the case evidence..."
        ):

            try:

                answer = ask_case_question(
                    selected_case,
                    question
                )

                st.session_state[
                    f"answer_{selected_case['case_id']}"
                ] = answer

            except Exception as e:

                st.error(
                    "The AI could not answer the question."
                )

                st.caption(
                    f"Technical details: {e}"
                )

    else:

        st.warning(
            "Please enter a question first."
        )


answer_key = (
    f"answer_{selected_case['case_id']}"
)


if answer_key in st.session_state:

    st.markdown(
        "### AI Response"
    )

    st.write(
        st.session_state[
            answer_key
        ]
    )


# ============================================================
# SAFETY / TRUST MESSAGE
# ============================================================

st.divider()

st.caption(
    "⚠️ Prototype limitation: Risk scores are explainable triage "
    "heuristics based on the supplied synthetic indicators. "
    "They are not calibrated fraud probabilities. "
    "Final investigative decisions remain with the human investigator."
)