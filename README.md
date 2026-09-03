# Junior AI Investigator

## AI-First Case Review for Fraud Investigators

Junior AI Investigator is a working prototype designed to help insurance fraud investigators proactively triage referred claims before manual investigation begins.

Instead of requiring an investigator to open every case and manually interpret individual fraud signals, the prototype reviews the complete referral queue, prioritizes cases using an explainable risk framework, generates grounded AI assessments, and allows the human investigator to interact with and override the AI.

---

## Product Goal

The core job-to-be-done is:

> Help a fraud investigator quickly understand which referrals deserve immediate attention, why they were prioritized, what evidence supports the assessment, and what to investigate next.

The AI assists the investigator but does not make a final fraud determination.

---

## Key Features

### Proactive Investigation Queue

- Loads all 50 synthetic referral cases.
- Prioritizes cases as HIGH, MEDIUM, or LOW risk.
- Sorts higher-risk cases to the top of the investigator queue.
- Allows filtering by risk level.

### Explainable Triage

Each case includes:

- Explainable risk score.
- Risk level.
- Triggered fraud-style indicators.
- Recommended next action.
- Raw source signals.

The risk score is a transparent triage heuristic and is not presented as a calibrated probability of fraud.

### AI Case Assessment

The AI generates a concise investigator-facing assessment containing:

- Case assessment.
- Strongest evidence.
- Counter-evidence and uncertainty.
- Recommended next step.

The LLM is instructed to use only the supplied synthetic case data and not invent missing facts.

### Investigator Q&A

Investigators can ask natural-language follow-up questions such as:

- What should I investigate first?
- Why is this case high risk?
- What evidence reduces suspicion?
- What information is missing?

If requested information is not available in the case data, the assistant explicitly states that the available data does not provide the information.

### Human-in-the-Loop Review

The investigator can:

- Accept the AI assessment.
- Reject the AI assessment.
- Mark the case as needing more investigation.
- Add investigator notes.

Final investigative decisions always remain with the human investigator.

### Cross-Case Intelligence

The prototype checks the current referral queue for repeated claim numbers.

For example, claim number `LTC-2034786` occurs in both:

- Case C1001
- Case C1031

The system surfaces this relationship so that an investigator can review related referrals before making a final disposition.

A cross-case relationship is treated as an investigative signal, not proof of fraud.

---

## Architecture

The prototype uses a hybrid deterministic + LLM architecture.

```text
Synthetic Claims CSV
        |
        v
Explainable Risk Engine
        |
        v
Structured Case Evidence
        |
        v
Grounded LLM Reasoning
        |
        v
Investigator UI
        |
        v
Human Decision + Notes