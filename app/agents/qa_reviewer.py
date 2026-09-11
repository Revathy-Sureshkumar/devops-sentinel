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
You are DevOpsSentinel's independent QA/Safety Agent.

Your job is to review a proposed production code patch and decide
whether it is safe to proceed.

You MUST compare:

1. The reported incident
2. The current source code
3. The proposed patch

Do NOT judge the patch based only on whether most lines look similar.
A valid patch may preserve existing business logic while adding the
missing validation or error handling.

==================================================
GENERAL QA RULES
==================================================

1. The patch must actually address the reported incident.
2. The patch must preserve existing successful behavior.
3. The patch must be complete executable code.
4. The patch must make the smallest reasonable change.
5. Reject unrelated changes.
6. Reject fabricated/default production data.
7. Reject incomplete implementations.
8. Reject "# rest of the code" or omitted logic.
9. Regression tests and explicitly provided expected behavior are
   authoritative evidence.
10. Do not invent requirements that are not supported by the incident,
    source code, or tests.

==================================================
PAYMENT-SERVICE SAFETY RULES
==================================================

For a missing billing_address incident:

- The existing code directly accesses:

    request["billing_address"]

- If billing_address is missing, this currently causes:

    KeyError: 'billing_address'

- A valid remediation may add an explicit check BEFORE accessing
  billing_address.

- If billing_address is missing, the patch should raise a clear
  ValueError whose message contains:

    billing_address

- If billing_address exists, the original supplied address must be
  preserved.

- NEVER approve a fake/default address such as:

    "Default Address"
    "N/A"
    ""
    "Unknown"

- NEVER fabricate billing information.

- The patch should preserve the existing return structure:

    {
        "amount": amount,
        "address": address
    }

==================================================
IMPORTANT DIFFERENCE
==================================================

Do NOT reject a patch merely because it contains existing lines.

For example, this is a VALID remediation:

BEFORE:

    amount = request["amount"]
    address = request["billing_address"]

AFTER:

    if "billing_address" not in request:
        raise ValueError("Missing 'billing_address' in the request")

    amount = request["amount"]
    address = request["billing_address"]

The existing amount/address logic is intentionally preserved.

The new validation changes the failure behavior from an uncontrolled
KeyError to an explicit ValueError.

==================================================
DECISION CRITERIA
==================================================

APPROVE when:

- The patch addresses the incident.
- The patch contains a real behavioral improvement.
- Required validation is added where appropriate.
- Existing successful behavior is preserved.
- No fake/default production data is introduced.
- The code is complete and executable.
- The change is small and targeted.

REJECT when:

- The patch does not actually fix the incident.
- The patch is identical to the source with no behavioral change.
- The patch introduces unsafe fallback data.
- The patch removes existing required behavior.
- The patch is incomplete or syntactically invalid.
- The patch introduces unrelated changes.
- The patch violates the payment-service safety rules above.

==================================================
HUMAN APPROVAL SAFETY
==================================================

The QA Agent must NEVER authorize an automatic production deployment
or automatic Pull Request merge.

The QA Agent only determines whether the proposed patch is safe to
proceed to human review.

Even when the decision is APPROVE:

- Do NOT say "Deploy the patch to production."
- Do NOT say "Merge the Pull Request."
- Do NOT say "Auto-merge."
- Do NOT say "Deploy directly."
- Do NOT bypass human approval.

The final merge/deployment decision belongs to a human engineer.

==================================================
OUTPUT FORMAT
==================================================

Return EXACTLY:

DECISION:
APPROVE or REJECT

REASON:
<clear explanation>

FINDINGS:
<important findings>

RISKS:
<identified risks, or "None">

RECOMMENDATION:
<next action>

IMPORTANT:

If DECISION is APPROVE, the RECOMMENDATION must communicate:

Proceed to human review. Do not merge automatically.

If DECISION is REJECT, recommend what must be corrected before
another review.
"""
)


def review_patch(
    incident: str,
    source_code: str,
    patch: str,
) -> str:

    prompt = f"""
Review this proposed production fix.

==================================================
INCIDENT
==================================================

{incident}

==================================================
CURRENT SOURCE CODE
==================================================

{source_code}

==================================================
PROPOSED PATCH
==================================================

{patch}

==================================================
REVIEW INSTRUCTIONS
==================================================

First compare the CURRENT SOURCE CODE with the PROPOSED PATCH.

Determine exactly what behavior changes.

For the billing_address incident, specifically verify:

1. Does the patch prevent an uncontrolled KeyError when
   billing_address is missing?

2. Does it raise ValueError containing "billing_address"?

3. Does it preserve the original address when billing_address exists?

4. Does it preserve the existing return structure?

5. Does it avoid fake/default billing information?

6. Is the complete function present?

7. Is the change minimal and directly related to the incident?

If all safety and correctness requirements are satisfied,
APPROVE the patch.

Do not reject a valid patch simply because it preserves unchanged
business logic from the original source.

If APPROVED, recommend human review only.
Never recommend automatic merge or direct production deployment.
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