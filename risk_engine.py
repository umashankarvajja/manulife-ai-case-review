import pandas as pd


def calculate_risk(case):
    """
    Calculate an explainable triage risk score for one insurance claim.

    IMPORTANT:
    This is a prototype triage score, NOT a probability that fraud occurred.
    """

    score = 0
    reasons = []

    # Strong fraud-style indicators
    if case["duplicate_service_billed"] == 1:
        score += 20
        reasons.append("Duplicate service billed")

    if case["shared_contact_with_provider"] == 1:
        score += 20
        reasons.append("Member shares contact information with provider")

    if case["service_overlap_other_provider"] == 1:
        score += 15
        reasons.append("Service overlaps with another provider")

    if case["recent_policy_change_flag"] == 1:
        score += 10
        reasons.append("Recent policy change detected")

    # Unusual service frequency
    if case["weekly_visit_frequency"] > 8:
        score += 10
        reasons.append(
            f"High weekly visit frequency: {case['weekly_visit_frequency']} visits/week"
        )

    # Large distance between member and provider
    if case["member_provider_distance_miles"] > 50:
        score += 10
        reasons.append(
            f"Large member-provider distance: "
            f"{case['member_provider_distance_miles']} miles"
        )

    # High weekend billing
    if case["weekend_billing_ratio"] > 0.30:
        score += 10
        reasons.append(
            f"High weekend billing ratio: "
            f"{case['weekend_billing_ratio']:.0%}"
        )

    # Claim amount much higher than peers
    if case["amount_vs_peer_avg_pct"] > 40:
        score += 15
        reasons.append(
            f"Claim amount is {case['amount_vs_peer_avg_pct']}% above peer average"
        )

    # Large percentage of round-dollar billing
    if case["round_dollar_billing_ratio"] > 0.40:
        score += 10
        reasons.append(
            f"High round-dollar billing ratio: "
            f"{case['round_dollar_billing_ratio']:.0%}"
        )

    # Keep score between 0 and 100
    score = min(score, 100)

    # Convert numeric score into investigator-friendly risk level
    if score >= 60:
        risk_level = "HIGH"
        recommended_action = "Escalate for detailed investigator review"

    elif score >= 30:
        risk_level = "MEDIUM"
        recommended_action = "Review supporting evidence before disposition"

    else:
        risk_level = "LOW"
        recommended_action = "Likely lower priority; perform standard validation"

    return score, risk_level, reasons, recommended_action


def load_and_score_cases(csv_path="data/sample_cases_synthetic.csv"):
    """
    Load all cases from the CSV and calculate a triage assessment.
    """

    df = pd.read_csv(csv_path)

    results = []

    for _, case in df.iterrows():
        score, risk_level, reasons, recommended_action = calculate_risk(case)

        results.append(
            {
                "case_id": case["case_id"],
                "claim_number": case["claim_number"],
                "risk_score": score,
                "risk_level": risk_level,
                "reasons": reasons,
                "recommended_action": recommended_action,
            }
        )

    return pd.DataFrame(results)


if __name__ == "__main__":
    scored_cases = load_and_score_cases()

    print("\n===== AI CASE REVIEW - TRIAGE RESULTS =====\n")

    print(
        scored_cases[
            [
                "case_id",
                "claim_number",
                "risk_score",
                "risk_level",
            ]
        ].to_string(index=False)
    )

    print("\n===== RISK SUMMARY =====\n")

    print(scored_cases["risk_level"].value_counts())