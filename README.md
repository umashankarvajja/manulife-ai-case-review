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
---

## Why This Architecture?

The prototype uses a hybrid deterministic + LLM design.

The deterministic risk engine provides transparent and reproducible triage.

The LLM is used for:

- Evidence synthesis.
- Natural-language explanations.
- Investigator follow-up questions.

The LLM is not responsible for independently determining whether fraud occurred.

This separation makes the system easier to explain, easier to validate, and less likely to hallucinate.

---

## Risk Scoring

The supplied synthetic dataset contains fraud-style indicators but does not contain ground-truth fraud labels.

For that reason, the prototype uses a transparent heuristic scoring model rather than presenting the score as a trained fraud probability.

Example indicators include:

- Duplicate service billing.
- Shared contact information with provider.
- Service overlap with another provider.
- Recent policy change.
- High weekly visit frequency.
- Large member-provider distance.
- High weekend billing.
- Claim amount significantly above peer average.
- High round-dollar billing.

### Prototype Risk Levels

- HIGH: 60–100
- MEDIUM: 30–59
- LOW: 0–29

In a production environment, these thresholds and weights would be calibrated using historical investigator outcomes, confirmed fraud labels, and business risk tolerances.

---

## AI Guardrails

The AI is instructed to:

1. Use only the supplied case evidence.
2. Never claim that fraud definitely occurred.
3. Clearly distinguish indicators from conclusions.
4. Explicitly identify unavailable information.
5. Avoid inventing provider, member, medical, policy, or criminal-history information.
6. Keep the investigator responsible for the final decision.

Example hallucination test:

Question:

> Has this provider ever been arrested?

Expected response:

> The available case data does not provide that information.

---

## Technology Stack

- Python
- Streamlit
- Pandas
- OpenAI API
- python-dotenv

---

## Project Structure

```text
MANULIFE_AI_CASE_REVIEW/
│
├── data/
│   └── sample_cases_synthetic.csv
│
├── app.py
├── risk_engine.py
├── ai_engine.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

The `.env` file contains the local API key and must not be committed to source control.

---

## Local Setup

Follow the steps below to run the Junior AI Investigator prototype locally.

### 1. Clone the repository

```bash
git clone <repository-url>
```

Then move into the project folder:

```bash
cd manulife-ai-case-review
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install required packages

```bash
pip install -r requirements.txt
```

### 4. Configure the OpenAI API key

Create a file named:

```text
.env
```

Add:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

Replace `your_openai_api_key_here` with a valid OpenAI API key.

Do not commit the `.env` file.

### 5. Start the application

```bash
streamlit run app.py
```

### 6. Open the application

Streamlit should automatically open the app in your browser.

If it does not, open:

```text
http://localhost:8501
```

---

## Suggested Demo Cases

### High Risk

`C1024`

Use this case to demonstrate:

- Multiple strong indicators.
- High-risk prioritization.
- AI assessment.
- Recommended investigation steps.

### Medium Risk

`C1050`

Use this case to demonstrate:

- Mixed evidence.
- Counter-evidence.
- Appropriate uncertainty.

### Low Risk

`C1002`

Use this case to demonstrate:

- Limited suspicious evidence.
- Lower-priority triage.
- Standard validation recommendation.

### Cross-Case Intelligence

`C1001` and `C1031`

Both contain the claim number:

`LTC-2034786`

This demonstrates queue-level relationship detection.

---

## Prototype Trade-Offs

The prototype intentionally does not include:

- Authentication.
- Production databases.
- Enterprise system integrations.
- Deployment pipelines.
- Multi-tenant architecture.
- Complex multi-agent orchestration.

The goal was to polish the core AI-assisted investigator workflow rather than build production infrastructure.

---

## Production Evolution

With additional time and production data, I would add:

- Historical investigator outcomes.
- Confirmed fraud labels.
- Calibrated risk probabilities.
- Provider network analysis.
- Policy and document retrieval.
- Claim document ingestion.
- Audit logging.
- Prompt and model evaluation.
- Drift monitoring.
- Cost and latency monitoring.
- Role-based access controls.
- Enterprise claim-system integrations.

---

## Human-in-the-Loop Principle

The AI is designed as a Junior AI Investigator.

It performs the initial analytical work, organizes evidence, identifies uncertainty, and recommends investigative actions.

The human investigator remains responsible for validating evidence and making the final case disposition.