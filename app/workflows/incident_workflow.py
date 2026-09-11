import re

from app.agents.investigator import investigate
from app.agents.qa_reviewer import review_patch

from app.tools.repository import read_file
from app.tools.patch import apply_file_patch, run_tests

from app.tools.github import (
    create_incident_branch,
    commit_file,
    create_pull_request,
)

MAX_REVISIONS = 3


def extract_patch(result: str) -> str:
    """Extract PATCH from investigator response."""

    # XML-style format: <patch>...</patch>
    match = re.search(
        r"<patch>\s*(.*?)\s*</patch>",
        result,
        re.DOTALL | re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    # Plain-text format: PATCH: ... ASSUMPTIONS:
    match = re.search(
        r"PATCH:\s*(.*?)(?=\nASSUMPTIONS:|\Z)",
        result,
        re.DOTALL | re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return ""


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

    # Fallback for generic fenced code
    match = re.search(
        r"```\s*(.*?)```",
        patch,
        re.DOTALL,
    )

    if match:
        return match.group(1).strip()

    return ""


def run_incident_workflow(incident: str) -> None:

    print("\n========================================")
    print("      DEVOPS SENTINEL WORKFLOW")
    print("========================================\n")

    # ---------------------------------------------------------
    # INVESTIGATOR
    # ---------------------------------------------------------

    print("🔎 Investigator Agent: analyzing incident...\n")

    investigation = investigate(incident)

    print("=== INVESTIGATION ===")
    print(investigation)

    patch = extract_patch(investigation)

    if not patch:
        print("\n❌ Investigator did not return a usable patch.")
        return

    # ---------------------------------------------------------
    # FILE IDENTIFICATION
    # ---------------------------------------------------------

    file_path = extract_file_path(incident)

    if not file_path:
        print("\n❌ Could not identify the source file.")
        return

    print(f"\n📄 Target file: {file_path}")

    source_code = read_file(file_path)

    # ---------------------------------------------------------
    # QA + REVISION LOOP
    # ---------------------------------------------------------

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

        # -----------------------------------------------------
        # REJECT → INVESTIGATOR REVISION
        # -----------------------------------------------------

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

IMPORTANT:
- Make the smallest safe production fix.
- Do not invent fake/default values for required fields.
- Do not use values such as "Default Address" or "N/A".
- Preserve existing business logic.
- Return the COMPLETE replacement function.
- Do NOT use comments such as "# rest of the code".
- Preserve the existing return structure.
- Return executable Python code inside PATCH.

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

            if not patch:
                print("\n❌ Revised investigation did not contain a patch.")
                return

            continue

        # -----------------------------------------------------
        # APPROVE → APPLY PATCH
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # REGRESSION TESTS
        # -----------------------------------------------------

        print("\n🧪 Running regression tests...\n")

        test_result = run_tests()

        print(test_result)

        if test_result.startswith("TESTS PASSED"):

            print("\n🎉 INCIDENT REMEDIATION SUCCESSFUL")
            print("✅ Patch applied")
            print("✅ Regression tests passed")

            # -------------------------------------------------
            # GITHUB BRANCH
            # -------------------------------------------------

            print("\n🐙 Creating GitHub incident branch...")

            branch_name = create_incident_branch()

            print(f"✅ Branch created: {branch_name}")

            # Read final updated source
            updated_source = read_file(file_path)

            # -------------------------------------------------
            # GITHUB COMMIT
            # -------------------------------------------------

            print("\n📤 Committing remediation patch...")

            commit_result = commit_file(
                branch_name=branch_name,
                file_path=file_path,
                file_content=updated_source,
                commit_message="fix: remediate production incident",
            )

            print(f"📝 Commit: {commit_result}")

            # -------------------------------------------------
            # GITHUB PULL REQUEST
            # -------------------------------------------------

            print("\n🔀 Creating Pull Request...")

            pr_result = create_pull_request(
                branch_name=branch_name,
                title="fix: remediate production payment incident",
                body=f"""
## 🚨 DevOpsSentinel Automated Remediation

### Incident

{incident}

### Investigation

{investigation}

### QA Review

{qa_result}

### Validation

- ✅ QA/Safety Agent approved
- ✅ Patch applied
- ✅ Regression tests passed

### Human Approval Required

This PR was created automatically by DevOpsSentinel.

Please review the generated code before merging.
""",
            )

            print(f"🔗 Pull Request: {pr_result}")

            print("\n========================================")
            print("       REMEDIATION COMPLETE")
            print("========================================")

            print(f"🌿 Branch: {branch_name}")
            print(f"📝 Commit: {commit_result}")
            print(f"🔗 Pull Request: {pr_result}")

            print("\n👤 Human approval required before merge.")

            return

        # -----------------------------------------------------
        # TEST FAILURE → INVESTIGATOR
        # -----------------------------------------------------

        print("\n❌ Regression tests failed.")
        print("🔄 Sending test failure back to Investigator...\n")

        source_code = read_file(file_path)

        revision_prompt = f"""
The patch was approved by the QA/Safety Agent,
but the regression tests failed after the patch was applied.

INCIDENT:

{incident}

UPDATED SOURCE CODE:

{source_code}

PATCH:

{patch}

TEST RESULT:

{test_result}

Investigate the failure and create a corrected patch.

IMPORTANT:
- Preserve existing functionality.
- Do not introduce fake/default production data.
- Make the smallest safe correction.
- Return the COMPLETE replacement function.
- Do NOT use "# rest of the code".
- Preserve the existing return structure.
- Return executable Python code inside PATCH.

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

        if not patch:
            print("\n❌ Investigator did not return a usable patch.")
            return

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