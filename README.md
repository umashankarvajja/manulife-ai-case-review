# Junior AI Investigator

## AI-First Case Review for Fraud Investigators

**Junior AI Investigator** is a working prototype designed to help insurance fraud investigators proactively triage referred claims before manual investigation begins.

Instead of requiring an investigator to open every referral individually and manually interpret multiple fraud-style signals, the prototype reviews the referral queue, prioritizes cases using an explainable triage framework, generates grounded AI assessments, and allows the human investigator to interact with, validate, and override the AI.

The application is intentionally designed as a **decision-support tool**, not an autonomous fraud determination system.

---

## Product Goal

The core job-to-be-done is:

> Help a fraud investigator quickly understand which referrals deserve immediate attention, why they were prioritized, what evidence supports the assessment, what information is still missing, and what to investigate next.

The AI performs the initial analytical work, while the **human investigator remains responsible for the final case disposition**.

---

## Problem Being Solved

In a traditional reactive workflow, investigators may need to:

- Open referrals one at a time.
- Manually review many claim and fraud-style indicators.
- Decide independently which signals are meaningful.
- Spend significant time investigating cases that eventually appear benign.
- Repeat the same reasoning process across a large queue.

Junior AI Investigator changes the workflow from **reactive case lookup** to **proactive AI-assisted triage**.

Before the investigator begins reviewing a case, the prototype has already:

- Evaluated the case indicators.
- Assigned an explainable triage priority.
- Identified the strongest signals.
- Recommended a next action.
- Prepared the case for AI-assisted follow-up questions.

---

## Key Features

### 1. Proactive Investigation Queue

The application:

- Loads all **50 synthetic referral cases** from the supplied CSV.
- Evaluates every case before investigator review.
- Prioritizes referrals as **HIGH, MEDIUM, or LOW** risk.
- Sorts higher-priority cases to the top of the queue.
- Allows investigators to filter the queue by risk level.
- Allows investigators to select and drill into an individual case.

This gives the investigator a prioritized starting point instead of a raw list of referrals.

---

### 2. Explainable Triage

Each case includes:

- Explainable risk score.
- Risk level.
- Triggered fraud-style indicators.
- Recommended next action.
- Full raw case signals.

The risk score is intentionally presented as a **transparent triage heuristic**, not as a calibrated probability that fraud occurred.

---

### 3. AI-Generated Case Assessment

For a selected case, the investigator can generate an AI assessment containing:

- **Assessment** — a concise explanation of the case priority.
- **Strongest Evidence** — the most important indicators driving concern.
- **Counter-Evidence / Uncertainty** — mitigating evidence and missing information.
- **Recommended Next Step** — a concrete investigative action.

The LLM receives structured case evidence and is instructed to reason only from the available synthetic data.

---

### 4. Investigator Q&A

Investigators can ask natural-language follow-up questions about the selected case.

Example questions include:

- What should I investigate first?
- Why is this case considered high risk?
- What evidence reduces suspicion?
- What information is missing?
- Which indicators are most important?

The assistant is instructed to answer using only the available case evidence.

If the requested information is unavailable, it explicitly says so instead of inventing an answer.

Example:

**Question**

> Has this provider ever been arrested?

**Expected behavior**

> The available case data does not provide that information.

---

### 5. Human-in-the-Loop Review

The investigator can:

- Mark the case as **Needs More Investigation**.
- **Accept AI Assessment**.
- **Reject AI Assessment**.
- Add investigator notes.
- Save the current review decision during the application session.

The AI recommends and explains; the investigator decides.

> Prototype note: investigator decisions and notes are currently stored only in the active Streamlit session and are not persisted to a production database.

---

### 6. Cross-Case Intelligence

The prototype also performs a simple queue-level relationship check.

It detects when the same claim number appears in multiple referrals.

For example, claim number:

`LTC-2034786`

appears in:

- `C1001`
- `C1031`

When either case is opened, the application surfaces the related referral and recommends reviewing the relationship before final disposition.

This demonstrates that the assistant can provide value beyond analyzing cases independently.

A repeated claim number is treated as an **investigative relationship signal**, not proof of fraud.

---

## Architecture

The prototype uses a **hybrid deterministic + LLM architecture**.

```text
50 Synthetic Claims
        |
        v
CSV Ingestion with Pandas
        |
        v
Explainable Risk / Evidence Engine
        |
        v
Structured Case Evidence
        |
        v
Grounded LLM Reasoning
        |
        +----------------------+
        |                      |
        v                      v
AI Case Assessment      Investigator Q&A
        |                      |
        +----------+-----------+
                   |
                   v
          Investigator UI
                   |
                   v
       Human Decision + Notes
```

---

## Why This Architecture?

I deliberately chose a hybrid architecture rather than allowing an LLM to independently determine whether a referral is fraudulent.

### Deterministic Layer

The deterministic risk engine:

- Applies explicit and inspectable rules.
- Produces reproducible results.
- Identifies exactly which signals influenced the score.
- Creates structured evidence for the AI.

### LLM Layer

The LLM is used for tasks where natural-language reasoning adds value:

- Synthesizing evidence.
- Explaining why a referral was prioritized.
- Describing uncertainty.
- Recommending investigative next steps.
- Answering investigator follow-up questions.

### Human Layer

The investigator:

- Reviews the evidence.
- Challenges the AI.
- Accepts or rejects its assessment.
- Adds notes.
- Makes the final decision.

This separation improves **explainability, grounding, auditability, and human trust**.

---

## Risk Scoring

The supplied synthetic dataset contains fraud-style indicators but does **not** contain ground-truth fraud labels.

For that reason, the prototype does not claim that its score represents a trained probability of fraud.

Instead, it uses an intentionally transparent heuristic scoring system for **triage prioritization**.

### Prototype Scoring Rules

| Indicator | Prototype Rule | Points |
|---|---:|---:|
| Duplicate service billed | Triggered | +20 |
| Shared contact with provider | Triggered | +20 |
| Service overlap with another provider | Triggered | +15 |
| Recent policy change | Triggered | +10 |
| Weekly visit frequency | Greater than 8 | +10 |
| Member-provider distance | Greater than 50 miles | +10 |
| Weekend billing ratio | Greater than 30% | +10 |
| Amount vs. peer average | Greater than 40% above peers | +15 |
| Round-dollar billing ratio | Greater than 40% | +10 |

The score is capped at **100**.

### Prototype Risk Levels

- **HIGH:** 60–100
- **MEDIUM:** 30–59
- **LOW:** 0–29

The dataset also includes other contextual information, such as prior claims, that can be shown to the investigator without necessarily contributing directly to the prototype score.

### Production Approach

In a production environment, the weights and thresholds would not be treated as fixed expert truth.

They should be calibrated and validated using:

- Historical investigation outcomes.
- Confirmed fraud and non-fraud labels.
- Business loss severity.
- Investigator feedback.
- False-positive and false-negative costs.
- Precision/recall trade-offs.
- Risk appetite and operational capacity.

---

## AI Grounding and Guardrails

The AI is instructed to:

1. Use only the supplied case evidence.
2. Never state that fraud definitely occurred.
3. Distinguish indicators from conclusions.
4. Explicitly identify missing information.
5. Avoid inventing provider history.
6. Avoid inventing member history.
7. Avoid inventing medical records.
8. Avoid inventing criminal-history information.
9. Avoid inventing policy information not present in the case.
10. Keep the human investigator responsible for the final decision.

The LLM receives the selected case attributes, calculated triage level, detected indicators, and recommended triage action as structured context.

---

## Hallucination Guardrail Example

A simple adversarial test was performed during prototype validation.

**Question**

> Has this provider ever been arrested?

The dataset does not contain criminal-history information.

The assistant correctly responds that:

> The available case data does not provide that information.

This demonstrates the intended behavior when a question cannot be answered from the supplied evidence.

---

## Technology Stack

- **Python** — application and reasoning logic.
- **Streamlit** — lightweight investigator user interface.
- **Pandas** — CSV ingestion and structured case processing.
- **OpenAI API** — grounded case assessment and investigator Q&A.
- **python-dotenv** — local environment-variable management.
- **Git / GitHub** — version control and private repository delivery.

---

## Project Structure

```text
manulife-ai-case-review/
│
├── data/
│   └── sample_cases_synthetic.csv
│
├── app.py
├── risk_engine.py
├── ai_engine.py
├── requirements.txt
├── README.md
└── .gitignore
```

A local `.env` file must also be created to store the API key:

```text
.env
```

The `.env` file is intentionally excluded from GitHub through `.gitignore` and must never be committed to source control.

The local Python virtual environment (`venv/`) is also excluded from source control.

---

## Local Setup

Follow the steps below to run the Junior AI Investigator locally.

### Prerequisites

You will need:

- Python 3 installed.
- Git installed.
- Access to this private GitHub repository.
- A valid OpenAI API key with API access.

---

### 1. Clone the Private Repository

Open a terminal and run:

```bash
git clone https://github.com/umashankarvajja/manulife-ai-case-review.git
```

Move into the repository:

```bash
cd manulife-ai-case-review
```

Because the repository is private, your GitHub account must first be granted access.

---

### 2. Create a Python Virtual Environment

#### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

---

### 3. Install Required Packages

Run:

```bash
pip install -r requirements.txt
```

The project requires:

- Streamlit
- Pandas
- OpenAI
- python-dotenv

---

### 4. Configure the OpenAI API Key

Create a file named:

```text
.env
```

in the project root.

Add:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

Replace:

```text
your_openai_api_key_here
```

with a valid OpenAI API key.

Do not commit this file to GitHub.

---

### 5. Start the Application

Run:

```bash
streamlit run app.py
```

---

### 6. Open the Application

Streamlit should automatically open the application in your browser.

If it does not, manually open:

```text
http://localhost:8501
```

---

## Suggested Demo Cases

The following cases demonstrate the main behaviors of the prototype.

### High-Risk Case

`C1024`

Useful for demonstrating:

- HIGH risk prioritization.
- Multiple mutually reinforcing indicators.
- Explainable evidence.
- AI-generated assessment.
- Investigator Q&A.
- Recommended escalation.

---

### Medium-Risk Case

`C1050`

Useful for demonstrating:

- Mixed evidence.
- Duplicate-service concerns.
- Counter-evidence.
- Appropriate uncertainty.
- A recommendation for additional validation rather than an unsupported fraud conclusion.

---

### Low-Risk Case

`C1002`

Useful for demonstrating:

- Few or no strong fraud-style indicators.
- LOW priority.
- Counter-evidence.
- Standard validation recommendation.
- The AI's ability to avoid exaggerating risk.

---

### Cross-Case Intelligence

`C1001` and `C1031`

Both contain:

`LTC-2034786`

This is useful for demonstrating queue-level relationship detection.

`C1001` appears low risk when evaluated independently, while the related `C1031` referral is high risk.

The system surfaces the relationship for investigator review without treating the relationship itself as proof of fraud.

---

## Prototype Validation

The working slice was manually tested across multiple scenarios.

| Test | Case / Question | Expected Behavior |
|---|---|---|
| High-risk triage | `C1024` | HIGH priority with strong supporting evidence |
| Medium-risk triage | `C1050` | MEDIUM priority with mixed evidence |
| Low-risk triage | `C1002` | LOW priority without exaggerated suspicion |
| Cross-case relationship | `C1001` / `C1031` | Repeated claim number is surfaced |
| Grounded Q&A | "What should I investigate first?" | Evidence-based investigative recommendation |
| Hallucination test | "Has this provider ever been arrested?" | States that the data does not provide this information |
| Human override | Accept / Reject / Needs More Investigation | Investigator remains in control |

---

## Prototype Trade-Offs

The prototype intentionally does **not** include:

- Authentication.
- Role-based access control.
- Production databases.
- Persistent investigator-note storage.
- Enterprise claim-system integrations.
- External provider intelligence.
- Public-record searches.
- Deployment pipelines.
- Multi-tenant infrastructure.
- Complex multi-agent orchestration.

These were deliberately excluded so that the prototype could focus on the core AI-first investigator experience.

The design principle was:

> Polish a narrow, explainable, useful workflow rather than partially implementing many production features.

---

## Why Not a Multi-Agent System?

A multi-agent architecture was intentionally not used for this working slice.

The supplied input is small, structured, and narrow in scope. Adding multiple specialized agents would increase:

- Complexity.
- Latency.
- Cost.
- Debugging difficulty.
- Failure modes.

without providing enough additional value for the 50-case prototype.

The current architecture keeps deterministic triage separate from language-model reasoning and is easier to explain and validate.

With richer enterprise data and external tools, specialized agents or tool-calling workflows could become appropriate.

---

## Production Evolution

With additional time, historical data, and enterprise integrations, I would extend the system with:

### Data and Investigation Context

- Historical investigator outcomes.
- Confirmed fraud labels.
- Provider history.
- Member history.
- Provider network relationships.
- Claim documents.
- Medical authorization data.
- Policy and coverage information.
- Prior related referrals.

### AI and Retrieval

- Policy/document retrieval.
- Claim-document ingestion.
- Tool calling.
- Provider network queries.
- Case-history retrieval.
- Structured evidence citations.

### Model Evaluation

- Precision and recall measurement.
- False-positive analysis.
- False-negative analysis.
- Risk calibration.
- Prompt evaluation.
- Hallucination testing.
- Regression test suites.
- Investigator usefulness metrics.

### Governance and Trust

- Complete audit logging.
- Model/version tracking.
- Prompt/version tracking.
- Explainability records.
- Human override tracking.
- Responsible-AI controls.
- Access controls.

### Operations

- Persistent database storage.
- Enterprise authentication.
- API-based claim-system integrations.
- Cost monitoring.
- Latency monitoring.
- Model drift monitoring.
- Observability.
- Production deployment infrastructure.

---

## Scaling Beyond 50 Cases

For the prototype, all 50 cases can be processed locally.

At production scale, I would separate the system into asynchronous stages:

```text
Incoming Referral Queue
        |
        v
Batch / Event Processing
        |
        v
Risk Feature Computation
        |
        v
AI Assessment Generation
        |
        v
Structured Assessment Store
        |
        v
Investigator Application
```

Assessments could be generated before the investigator begins work so that investigators open an already-prioritized queue rather than waiting for real-time model calls.

Additional production considerations would include:

- Caching.
- Parallel processing.
- Rate limiting.
- Retry handling.
- Structured output validation.
- Model fallback strategies.
- Cost controls.
- Auditability.

---

## Key Design Principles

The prototype was built around five principles:

### 1. Proactive, Not Reactive

The AI reviews the queue before the investigator begins manual case review.

### 2. Explainable, Not Opaque

Investigators can see exactly which indicators influenced prioritization.

### 3. Grounded, Not Imaginative

The LLM is instructed to stay within the supplied evidence and explicitly acknowledge missing information.

### 4. Assistive, Not Autonomous

The AI recommends investigative actions but does not determine that fraud occurred.

### 5. Human-Controlled

Investigators can challenge, override, annotate, and ultimately decide what happens to a case.

---

## Human-in-the-Loop Principle

The AI is designed as a **Junior AI Investigator**.

It performs the initial analytical work by:

- Organizing case evidence.
- Identifying important indicators.
- Highlighting uncertainty.
- Generating a concise assessment.
- Recommending investigative actions.
- Answering grounded follow-up questions.
- Surfacing simple cross-case relationships.

The human investigator remains responsible for:

- Validating evidence.
- Obtaining missing documentation.
- Challenging unsupported conclusions.
- Accepting or rejecting AI recommendations.
- Determining the final case disposition.

The intended relationship is:

```text
AI prepares the investigation.
Human investigator owns the decision.
```

---

## Disclaimer

This prototype uses entirely synthetic data and is intended only to demonstrate product thinking, AI system design, explainability, grounding, and human-in-the-loop case review.

The prototype risk scores are illustrative triage heuristics and must not be interpreted as validated fraud probabilities or production fraud determinations.