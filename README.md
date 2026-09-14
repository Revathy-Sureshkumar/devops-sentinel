# 🛡️ DevOpsSentinel

### From production incident to verified code fix — autonomously.

DevOpsSentinel is an AI-powered SRE agent that helps engineers investigate production incidents, identify root causes, generate code fixes, verify them with an independent QA agent, and create a GitHub Pull Request.

Instead of stopping at **"here's what went wrong"**, DevOpsSentinel takes the incident closer to **"here's a tested fix ready for review."**

---

## 🚨 The Problem

When a production incident occurs, engineers often have to manually:

1. Read the incident report
2. Check production logs
3. Analyze the stack trace
4. Find the relevant source code
5. Identify the root cause
6. Prepare a fix
7. Run tests
8. Create a Pull Request

A lot of this work is repetitive and takes valuable time during an incident.

**DevOpsSentinel automates this workflow while keeping the engineer in control of the final decision.**

---

## 💡 How It Works

```text
        ┌──────────────┐
        │ Jira Incident│
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Production   │
        │ Log Analysis │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Investigator │
        │    Agent     │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │  Root Cause  │
        │ Identification│
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │  Code Fix    │
        │  Generation  │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ QA / Safety  │
        │    Agent     │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Regression   │
        │    Tests     │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ GitHub Pull  │
        │   Request    │
        └──────┬───────┘
               ↓
        👤 Human Approval

🤖 Multi-Agent Architecture

DevOpsSentinel uses two specialized agents.

🔍 Investigator Agent

The Investigator Agent focuses on understanding the incident.

It can:

Analyze incident information
Inspect logs and stack traces
Search the repository
Read relevant source files
Identify the likely root cause
Generate a proposed remediation
🛡️ QA/Safety Agent

The QA/Safety Agent acts as an independent reviewer.

It checks whether the proposed fix:

Actually addresses the incident
Preserves existing behavior
Adds appropriate validation
Avoids unsafe fallback behavior
Is executable and reasonable

If the proposed fix is rejected, the workflow can revise the remediation before continuing.

🔄 End-to-End Workflow
Jira Incident
      ↓
Incident Detection
      ↓
Log + Stack Trace Analysis
      ↓
Repository Investigation
      ↓
Root Cause Analysis
      ↓
Code Fix Generation
      ↓
Independent QA/Safety Review
      ↓
Revision if Required
      ↓
Regression Tests
      ↓
Git Branch + Commit
      ↓
GitHub Pull Request
      ↓
Human Approval
🧪 Demo Incident

For our demonstration, DevOpsSentinel handles a payment-service failure.

Production Error
KeyError: 'billing_address'

The failure occurs when the payment service directly accesses:

address = request["billing_address"]

without validating whether the field exists.

DevOpsSentinel:

Receives the Jira incident
Retrieves the production log
Identifies the failing code
Determines the root cause
Generates a safe remediation
Sends the fix to the QA/Safety Agent
Runs the regression tests
Creates a GitHub Pull Request

The result is a tested code change ready for human review.

🛠️ Tech Stack
Technology	Purpose
Python	Core application and tools
Strands Agents SDK	Agent orchestration
Amazon Bedrock	AI reasoning
FastAPI	Incident/API layer
Jira API	Incident ingestion
GitHub API	Repository access and Pull Requests
Streamlit	Interactive SRE dashboard
Pytest	Regression testing
AWS	Cloud/AI infrastructure
📁 Project Structure
devops-sentinel/
│
├── app/
│   ├── agents/
│   │   ├── investigator.py
│   │   ├── qa_reviewer.py
│   │   └── incident_detector.py
│   │
│   ├── tools/
│   │   ├── repository.py
│   │   ├── patch.py
│   │   ├── github.py
│   │   ├── jira.py
│   │   └── failure_injector.py
│   │
│   └── workflows/
│       └── incident_workflow.py
│
├── frontend/
│   └── streamlit_app.py
│
├── demo/
│   ├── fixtures/
│   │   └── payment_buggy.py
│   └── logs/
│       └── payment-service-error.log
│
├── tests/
│   └── test_payment.py
│
├── .env
├── .gitignore
└── README.md
⚙️ Setup
1. Clone the repository
git clone https://github.com/Revathy-Sureshkumar/devops-sentinel.git
cd devops-sentinel
2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate

On Windows:

.venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables

Create a .env file:

AWS_REGION=ap-south-1
BEDROCK_MODEL_ID=apac.amazon.nova-pro-v1:0

GITHUB_OWNER=your-github-username
GITHUB_REPO=your-repository
GITHUB_TOKEN=your-github-token

JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email
JIRA_API_TOKEN=your-jira-api-token

Never commit .env or API tokens to GitHub.

▶️ Run the Dashboard

Start the Streamlit application:

streamlit run frontend/streamlit_app.py

Then open the URL shown by Streamlit, usually:

http://localhost:8501

Enter a Jira incident URL and click:

🚨 Resolve Incident

🧪 Run Tests

Run the regression tests with:

pytest

For the demo payment service:

python -m pytest tests/test_payment.py -v
🔐 Human-in-the-Loop

DevOpsSentinel is designed with controlled autonomy.

The agent can:

Investigate → Generate → Review → Test → Create PR

But it does not automatically merge the change into production.

The engineer remains responsible for the final approval.

This gives us a balance between:

AI automation + engineering control

🌟 Why DevOpsSentinel?

Traditional incident tooling often focuses on:

Detect → Alert → Investigate

DevOpsSentinel takes the workflow further:

Detect → Investigate → Fix → Review → Test → Pull Request → Human Approval

The goal is not to replace SRE engineers.

The goal is to give them back the time they spend on repetitive incident work.

🚀 Future Improvements

We plan to extend DevOpsSentinel with:

Support for more incident types
Additional observability integrations
Stronger root-cause analysis
More comprehensive patch validation
Expanded automated testing
Richer incident history and audit trails
Additional collaboration and notification integrations
👥 Built For

DevOps and SRE teams that want to reduce the time spent on repetitive incident investigation and remediation while keeping humans in control of production changes.

📌 Project

DevOpsSentinel

Let the AI handle the repetitive work. Let the engineer make the important decisions.


### One important thing

Before you paste this into GitHub, **don't include any actual AWS, GitHub, or Jira credentials**. Your `.env` is already ignored, so keep it that way.

Also, I would **not mention Slack as a completed feature** in the README unless your submitted version actually has the Slack integration working. That keeps your README completely defensible during judging.

For the hackathon, this README gives judges the important story immediately:

**Problem → Solution → Architecture → Real Demo → Tech Stack → Setup → Safety → Future.**
