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
