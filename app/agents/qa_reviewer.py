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


qa_reviewer = Agent(
    model=model,
    system_prompt="""
You are DevOpsSentinel's QA/Safety Agent.

Your job is to independently review a proposed code fix created by
another AI agent.

Review the proposed fix for:

1. Correctness
2. Whether it actually addresses the reported incident
3. Regression risk
4. Consistency with the provided source code
5. Unnecessary or unrelated changes
6. Error-handling behavior
7. Security and operational risks

Important rules:

- Do not blindly approve the proposed patch.
- Use only the evidence provided.
- Clearly identify assumptions.
- Reject the patch when important information is missing or
  the proposed behavior is potentially unsafe.
- Prefer small, targeted fixes.

Return EXACTLY this structure:

DECISION:
APPROVE or REJECT

REASON:

FINDINGS:

RISKS:

RECOMMENDATION:
"""
)


def review_patch(incident: str, source_code: str, patch: str) -> str:
    prompt = f"""
Review the following proposed production fix.

=== INCIDENT ===
{incident}

=== SOURCE CODE ===
{source_code}

=== PROPOSED PATCH ===
{patch}

Independently evaluate whether this patch should proceed.
"""

    response = qa_reviewer(prompt)
    return str(response)


if __name__ == "__main__":
    incident = """
Service: payment-service
Severity: HIGH

Error:
KeyError: 'billing_address'

The payment request is missing the billing_address field.
"""

    source_code = """
def process_payment(request):
    amount = request["amount"]
    address = request["billing_address"]

    return {
        "amount": amount,
        "address": address
    }
"""

    patch = """
def process_payment(request):
    if "billing_address" not in request:
        raise ValueError("Missing 'billing_address' in the request")

    amount = request["amount"]
    address = request["billing_address"]

    return {
        "amount": amount,
        "address": address
    }
"""

    result = review_patch(
        incident=incident,
        source_code=source_code,
        patch=patch,
    )

    print("\n=== DevOpsSentinel QA/Safety Review ===\n")
    print(result)