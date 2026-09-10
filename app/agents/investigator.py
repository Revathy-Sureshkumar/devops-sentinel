import os

from dotenv import load_dotenv
from strands import Agent, tool
from strands.models import BedrockModel

from app.tools.repository import list_files, read_file, search_code


load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

if not MODEL_ID:
    raise ValueError("BEDROCK_MODEL_ID is not set in .env")


@tool
def repository_list_files() -> str:
    """List files available in the project repository."""
    return list_files()


@tool
def repository_read_file(file_path: str) -> str:
    """Read a text file from the project repository.

    Args:
        file_path: Relative path of the file to read.
    """
    return read_file(file_path)


@tool
def repository_search_code(query: str) -> str:
    """Search the repository for a text string.

    Args:
        query: Text to search for.
    """
    return search_code(query)


model = BedrockModel(
    model_id=MODEL_ID,
    region_name=AWS_REGION,
)


investigator = Agent(
    model=model,
    tools=[
        repository_list_files,
        repository_read_file,
        repository_search_code,
    ],
    system_prompt="""
You are DevOpsSentinel's Investigator Agent.

Your job is to investigate production incidents using the repository
tools available to you.

When an incident is provided:

1. Understand the error and stack trace.
2. Search the repository for the affected symbol, error, or file.
3. Read the relevant source file.
4. Inspect enough surrounding code to understand the failure.
5. Determine the most likely root cause.
6. Generate a targeted code-level fix.
7. Provide a patch based on the ACTUAL repository contents.

Important rules:

- Use repository tools before proposing a code patch whenever
  relevant source code is available.
- Do not invent source code.
- Do not claim to have inspected a file unless you actually read it.
- Clearly distinguish confirmed findings from assumptions.
- Prefer small, targeted changes.
- Do not approve your own patch. A separate QA/Safety Agent will review it.

Return your response in this format:

ROOT CAUSE:
IMPACT:
EVIDENCE:
FIX:
PATCH:
ASSUMPTIONS:
"""
)


def investigate(incident: str) -> str:
    """Investigate a production incident."""
    response = investigator(incident)
    return str(response)


if __name__ == "__main__":
    incident = """
Production Incident

Service: payment-service
Severity: HIGH

Error:
KeyError: 'billing_address'

Stack Trace:
Traceback (most recent call last):
  File "demo/sample_repo/app/services/payment.py", line 3, in process_payment
    address = request["billing_address"]
KeyError: 'billing_address'
"""

    result = investigate(incident)

    print("\n=== DevOpsSentinel Investigator ===\n")
    print(result)