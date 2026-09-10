import re

from app.agents.investigator import investigate
from app.agents.qa_reviewer import review_patch
from app.tools.repository import read_file
from app.tools.patch import apply_file_patch, run_tests


MAX_REVISIONS = 3


def extract_patch(result: str) -> str:
    """Extract the PATCH section from the investigator response."""
    match = re.search(
        r"PATCH:\s*(.*?)(?=\nASSUMPTIONS:|\Z)",
        result,
        re.DOTALL,
    )

    return match.group(1).strip() if match else ""


def extract_file_path(incident: str) -> str | None:
    """Extract the source file path from the incident."""
    patterns = [
        r'File "([^"]+)"',
        r"File '([^']+)'",
    ]

    for pattern in patterns:
        match = re.search(pattern, incident)
        if match:
            return match.group(1)

    return None


def extract_python_code(patch: str) -> str:
    """Extract Python code from a fenced code block."""
    match = re.search(
        r"```python\s*(.*?)```",
        patch,
        re.DOTALL | re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return ""


def run_incident_workflow(incident: str) -> None:
    print("\n========================================")
    print("      DEVOPS SENTINEL WORKFLOW")
    print("========================================\n")

    print("🔎 Investigator Agent: analyzing incident...\n")

    investigation = investigate(incident)

    print("=== INVESTIGATION ===")
    print(investigation)

    patch = extract_patch(investigation)

    file_path = extract_file_path(incident)

    if not file_path:
        print("\n❌ Could not identify the source file.")
        return

    source_code = read_file(file_path)

    for attempt in range(1, MAX_REVISIONS + 1):

        print(f"\n=== QA REVIEW — Attempt {attempt} ===\n")

        qa_result = review_patch(
            incident=incident,
            source_code=source_code,
            patch=patch,
        )

        print(qa_result)

        decision_match = re.search(
            r"DECISION:\s*(APPROVE|REJECT)",
            qa_result,
            re.IGNORECASE,
        )

        if not decision_match:
            print("\n❌ Could not determine QA decision.")
            return

        decision = decision_match.group(1).upper()

        # ---------------------------------------------------------
        # REJECT → SEND FEEDBACK BACK TO INVESTIGATOR
        # ---------------------------------------------------------
        if decision == "REJECT":

            if attempt == MAX_REVISIONS:
                print("\n❌ Maximum revision attempts reached.")
                print("➡️ Human engineer review required.")
                return

            print("\n🔄 Patch rejected.")
            print("↩️ Sending QA feedback to Investigator...\n")

            revision_prompt = f"""
The QA/Safety Agent rejected your proposed patch.

INCIDENT:
{incident}

SOURCE CODE:
{source_code}

PREVIOUS PATCH:
{patch}

QA REVIEW:
{qa_result}

Revise the patch using the QA feedback.

Use repository tools again when necessary.

Return:

ROOT CAUSE:
IMPACT:
EVIDENCE:
FIX:
PATCH:
ASSUMPTIONS:
"""

            investigation = investigate(revision_prompt)

            print("=== REVISED INVESTIGATION ===")
            print(investigation)

            patch = extract_patch(investigation)
            continue

        # ---------------------------------------------------------
        # APPROVE → APPLY PATCH
        # ---------------------------------------------------------
        print("\n✅ QA APPROVED PATCH")

        new_code = extract_python_code(patch)

        if not new_code:
            print("\n❌ Could not extract Python code from patch.")
            return

        print("\n🛠️ Applying patch...")

        patch_result = apply_file_patch(
            file_path=file_path,
            old_text=source_code,
            new_text=new_code,
        )

        print(patch_result)

        if patch_result.startswith("ERROR"):
            print("\n❌ Patch application failed.")
            return

        # ---------------------------------------------------------
        # RUN REGRESSION TESTS
        # ---------------------------------------------------------
        print("\n🧪 Running regression tests...\n")

        test_result = run_tests()

        print(test_result)

        if test_result.startswith("TESTS PASSED"):
            print("\n🎉 INCIDENT REMEDIATION SUCCESSFUL")
            print("✅ Patch applied")
            print("✅ Regression tests passed")
            print("➡️ Next step: GitHub integration")
            return

        # ---------------------------------------------------------
        # TEST FAILURE → SEND BACK TO INVESTIGATOR
        # ---------------------------------------------------------
        print("\n❌ Regression tests failed.")
        print("🔄 Sending test failure back to Investigator...\n")

        # Read the updated file after the failed patch.
        source_code = read_file(file_path)

        revision_prompt = f"""
The patch was approved by the QA/Safety Agent, but the regression
tests failed after the patch was applied.

INCIDENT:
{incident}

UPDATED SOURCE CODE:
{source_code}

PATCH:
{patch}

TEST RESULT:
{test_result}

Investigate the failure and create a corrected patch.

Use repository tools when necessary.

Return:

ROOT CAUSE:
IMPACT:
EVIDENCE:
FIX:
PATCH:
ASSUMPTIONS:
"""

        investigation = investigate(revision_prompt)

        print("=== INVESTIGATOR REVISION ===")
        print(investigation)

        patch = extract_patch(investigation)

    print("\n❌ Maximum workflow attempts reached.")
    print("➡️ Human engineer review required.")


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

    run_incident_workflow(incident)