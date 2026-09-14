# 🛡️ DevOpsSentinel

### From production incident to verified code fix — autonomously.

DevOpsSentinel is an AI-powered SRE agent that helps engineers investigate production incidents, identify root causes, generate code fixes, verify them with an independent QA/Safety Agent, and create a GitHub Pull Request.

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

This process is important, but much of the work is repetitive and takes valuable time during an incident.

We wanted to see if an AI agent could handle the repetitive parts while keeping the engineer in control of the final decision.

---

## 💡 How It Works

```text
Jira Incident
      ↓
Production Log Analysis
      ↓
Investigator Agent
      ↓
Root Cause Analysis
      ↓
Code Fix Generation
      ↓
QA / Safety Agent
      ↓
Regression Tests
      ↓
GitHub Branch + Commit
      ↓
GitHub Pull Request
      ↓
👤 Human Approval
```

---

## 🤖 Multi-Agent Architecture

DevOpsSentinel uses two specialized agents.

### 🔍 Investigator Agent

The Investigator Agent focuses on understanding the incident.

It:

- Analyzes incident information
- Inspects logs and stack traces
- Searches the repository
- Reads relevant source files
- Identifies the likely root cause
- Generates a proposed remediation

### 🛡️ QA/Safety Agent

The QA/Safety Agent acts as an independent reviewer.

It checks whether the proposed fix:

- Actually addresses the incident
- Preserves existing behavior
- Adds appropriate validation
- Avoids unsafe fallback behavior
- Is executable and reasonable

If the proposed fix is rejected, the workflow can revise the remediation before continuing.

The separation is intentional: **one agent proposes the solution, while another reviews it.**

---

## 🔄 End-to-End Workflow

```text
Jira Incident
      ↓
Incident Detection
      ↓
Production Log Analysis
      ↓
Repository Investigation
      ↓
Root Cause Analysis
      ↓
Code Fix Generation
      ↓
QA/Safety Review
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
```

---

## 🧪 Demo Incident

For our demonstration, DevOpsSentinel handles a payment-service failure.

### Production Error

```text
KeyError: 'billing_address'
```

The failure occurs when the payment service directly accesses:

```python
address = request["billing_address"]
```

without validating whether the field exists.

DevOpsSentinel receives the Jira incident and associated production log, investigates the failing code, identifies the root cause, and generates a remediation.

The proposed fix then goes through the QA/Safety Agent and regression tests.

Once verification succeeds, DevOpsSentinel creates a GitHub branch, commit, and Pull Request.

### Demo Flow

```text
Production Incident
        ↓
KeyError: 'billing_address'
        ↓
Root Cause Identified
        ↓
Code Fix Generated
        ↓
QA/Safety Review
        ↓
Tests Passed
        ↓
GitHub Pull Request
        ↓
Human Approval
```

The result is a **tested code change ready for human review**.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application and automation |
| Strands Agents SDK | Agent orchestration |
| Amazon Bedrock | AI reasoning |
| FastAPI | API and incident workflow layer |
| Jira API | Incident ingestion |
| GitHub API | Repository access, commits and Pull Requests |
| Streamlit | Interactive SRE dashboard |
| Pytest | Regression testing |
| AWS | Cloud and AI infrastructure |

---

## 📁 Project Structure

```text
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
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/Revathy-Sureshkumar/devops-sentinel.git
cd devops-sentinel
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure AWS Credentials

DevOpsSentinel uses Amazon Bedrock, so you need to authenticate with AWS before running the application.

If you use AWS CLI, log in with:

```bash
aws login
```

Then verify your AWS identity:

```bash
aws sts get-caller-identity
```

Make sure the authenticated AWS account has permission to use Amazon Bedrock in the configured region.

### 5. Configure environment variables

Create a `.env` file with your own credentials:

```env
AWS_REGION=ap-south-1
BEDROCK_MODEL_ID=apac.amazon.nova-pro-v1:0

GITHUB_OWNER=your-github-username
GITHUB_REPO=your-repository
GITHUB_TOKEN=your-github-token

JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email
JIRA_API_TOKEN=your-jira-api-token
```

**Never commit `.env` or API credentials to GitHub.**

---

## ▶️ Run the Dashboard

Start the Streamlit application:

```bash
streamlit run frontend/streamlit_app.py
```

Then open:

```text
http://localhost:8501
```

Enter a Jira incident URL in the dashboard and click:

**🚨 Resolve Incident**

DevOpsSentinel will start the incident remediation workflow.

---

## 🧪 Run Tests

Run the complete test suite:

```bash
pytest
```

For the payment-service demo:

```bash
python -m pytest tests/test_payment.py -v
```

---

## 🔐 Human-in-the-Loop

DevOpsSentinel is designed with controlled autonomy.

The system can:

```text
Investigate → Generate → Review → Test → Create PR
```

But it does **not automatically merge the change into production**.

The engineer remains responsible for the final approval.

This gives us a balance between:

**AI automation + engineering control**

---

## 🌟 Why DevOpsSentinel?

Traditional incident response often looks like:

```text
Detect → Alert → Investigate
```

DevOpsSentinel takes the workflow further:

```text
Detect
  ↓
Investigate
  ↓
Fix
  ↓
Review
  ↓
Test
  ↓
Pull Request
  ↓
Human Approval
```

The goal is not to replace SRE engineers.

The goal is to reduce the repetitive work they have to do during an incident.

---

## 🏆 What We're Proud Of

We wanted to build more than an AI chatbot that explains an error.

DevOpsSentinel demonstrates an end-to-end remediation workflow:

**Incident → Root Cause → Code Fix → QA Review → Testing → Pull Request**

The part we are most proud of is the independent QA/Safety layer.

The Investigator Agent proposes the solution, while the QA/Safety Agent reviews it before the change moves forward.

---

## 📚 What We Learned

Building DevOpsSentinel taught us that an effective AI agent needs more than a good prompt.

It needs:

- The right context
- Access to real tools
- A structured workflow
- Validation
- Clear boundaries
- Human oversight

We also learned that AI can be most useful when it works alongside engineers rather than trying to replace them.

The AI handles the repetitive investigation and remediation work, while the engineer stays responsible for important decisions.

---

## 🚀 What's Next

We want to extend DevOpsSentinel to handle more types of production incidents and connect it with additional DevOps and observability tools.

Future improvements include:

- Support for more incident types
- Additional observability integrations
- Stronger root-cause analysis
- More comprehensive patch validation
- Expanded automated testing
- Richer incident history and audit trails
- Additional collaboration and notification capabilities

---

## 👥 Built For

DevOps and SRE teams that want to reduce repetitive incident investigation and remediation while keeping humans in control of production changes.

---

## 📌 Project

**DevOpsSentinel**

> Let the AI handle the repetitive work. Let the engineer make the important decisions.
