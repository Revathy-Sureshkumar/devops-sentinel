import os

from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel


load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

if not MODEL_ID:
    raise ValueError("BEDROCK_MODEL_ID is not set in .env")


model = BedrockModel(
    model_id=MODEL_ID,
    region_name=AWS_REGION,
)


incident_detector = Agent(
    model=model,
    system_prompt="""
You are DevOpsSentinel's Production Incident Detection Agent.

Your job is to analyze production incident information obtained
from a support ticket and convert it into a clear production
incident report for an SRE engineer.

The input may contain:
1. A support ticket description
2. Production log telemetry
3. Ticket metadata

Use ONLY the information provided.

Do NOT investigate the root cause.
Do NOT generate a code patch.
Do NOT modify any files.

Your responsibility is ONLY to identify and structure the incident.

Extract the following when available:

- Service
- Severity
- Timestamp
- Environment
- Error
- File
- Line number
- Function
- Stack trace
- Incident summary

Rules:

- Prefer explicit information from the production log.
- Use the support ticket description to provide additional context.
- Do not invent information.
- If a field is unavailable, write:
  Not available
- Preserve the actual error message.
- Preserve the actual file path, line number and function when present.
- Do not propose a solution.
- Do not perform root-cause analysis.

Return the incident in exactly this format:

PRODUCTION INCIDENT

Service: <service>
Severity: <severity>
Timestamp: <timestamp>
Environment: <environment>

Error:
<error>

Location:
File: <file>
Line: <line>
Function: <function>

Stack Trace:
<stack trace>

Incident Summary:
<short explanation of what the telemetry shows>

Remember:
You are an incident detection and normalization agent.
The Investigator Agent will perform root-cause analysis later.
""",
)


def detect_incident(raw_log: str) -> str:
    """
    Analyze raw production telemetry and generate a structured
    production incident report.

    This function is kept compatible with the existing workflow.
    """

    response = incident_detector(
        f"""
Analyze the following raw production telemetry.

==================================================
RAW PRODUCTION LOG
==================================================

{raw_log}

==================================================
TASK
==================================================

Convert this telemetry into the required
PRODUCTION INCIDENT format.

Only use information supported by the telemetry.
Do not invent missing details.
Do not generate a fix or patch.
"""
    )

    return str(response)


def detect_jira_incident(
    description: str,
    log_content: str,
    issue_key: str = "Not available",
) -> str:
    """
    Convert Jira support-ticket information and its
    production log into a structured production incident.

    The Jira issue itself is retrieved by app.tools.jira.
    This function only performs incident normalization.
    """

    response = incident_detector(
        f"""
Analyze the following production incident received from Jira.

==================================================
JIRA ISSUE
==================================================

Issue Key:
{issue_key}

==================================================
SUPPORT TICKET DESCRIPTION
==================================================

{description}

==================================================
PRODUCTION LOG ATTACHMENT
==================================================

{log_content}

==================================================
TASK
==================================================

Convert this information into the required
PRODUCTION INCIDENT format.

Use the production log as the primary telemetry source.

Use the Jira description only to add incident context
when it is explicitly supported.

Only use information provided above.

Do not invent missing information.

Do not investigate the root cause.

Do not generate a code fix or patch.

Do not modify any files.
"""
    )

    return str(response)


if __name__ == "__main__":

    raw_log = """
2026-09-12T12:55:31Z ERROR payment-service
Environment: production
Severity: HIGH

Request processing failed.

Traceback (most recent call last):
  File "demo/sample_repo/app/services/payment.py", line 3,
  in process_payment
    address = request["billing_address"]

KeyError: 'billing_address'
"""

    result = detect_incident(raw_log)

    print("\n========================================")
    print("   DEVOPS SENTINEL INCIDENT DETECTOR")
    print("========================================\n")

    print(result)