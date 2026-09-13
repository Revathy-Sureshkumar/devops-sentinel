import re
from pathlib import Path

from app.agents.investigator import investigate
from app.agents.qa_reviewer import review_patch
from app.agents.incident_detector import detect_jira_incident

from app.tools.repository import read_file
from app.tools.patch import apply_file_patch, run_tests

from app.tools.github import (
    create_incident_branch,
    commit_file,
    create_pull_request,
)

from app.tools.jira import get_jira_incident


MAX_REVISIONS = 3


# =============================================================
# PATH RESOLUTION
# =============================================================

def resolve_repository_path(file_path: str) -> str:
    """
    Resolve a production/repository-relative file path to the
    local repository workspace used by the demo.

    Example:

        app/services/payment.py
            ↓
        demo/sample_repo/app/services/payment.py
    """

    path = Path(file_path)

    # Case 1:
    # The path already exists exactly as reported.
    if path.exists():
        return str(path)

    # Case 2:
    # Jira/production logs usually contain repository-relative
    # paths such as app/services/payment.py.
    demo_path = Path("demo/sample_repo") / path

    if demo_path.exists():
        return str(demo_path)

    # Case 3:
    # Return original path so the caller can report the
    # appropriate "file not found" error.
    return file_path


# =============================================================
# PATCH EXTRACTION
# =============================================================

def extract_patch(result: str) -> str:
    """Extract PATCH from investigator response."""

    # XML-style format:
    # <patch>...</patch>
    match = re.search(
        r"<patch>\s*(.*?)\s*</patch>",
        result,
        re.DOTALL | re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    # Plain-text format:
    # PATCH: ...
    # ASSUMPTIONS:
    match = re.search(
        r"PATCH:\s*(.*?)(?=\nASSUMPTIONS:|\Z)",
        result,
        re.DOTALL | re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return ""


# =============================================================
# FILE PATH EXTRACTION
# =============================================================

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


# =============================================================
# PYTHON CODE EXTRACTION
# =============================================================

def extract_python_code(patch: str) -> str:
    """
    Extract executable Python code from an investigator patch.

    Also normalizes escaped quotes returned by the model.
    """

    match = re.search(
        r"```python\s*(.*?)```",
        patch,
        re.DOTALL | re.IGNORECASE,
    )

    if not match:
        # Fallback for generic fenced code
        match = re.search(
            r"```\s*(.*?)```",
            patch,
            re.DOTALL,
        )

    if not match:
        return ""

    code = match.group(1).strip()

    # Models can sometimes return:
    #
    # raise ValueError(\"billing_address\")
    #
    # Convert this into valid Python:
    #
    # raise ValueError("billing_address")
    code = code.replace('\\"', '"')

    return code


# =============================================================
# EXISTING DEVOPS SENTINEL WORKFLOW
# =============================================================

def run_incident_workflow(incident: str) -> None:
    """
    Existing DevOpsSentinel remediation workflow.

    Investigator
        ↓
    QA / Safety
        ↓
    Patch
        ↓
    Regression Tests
        ↓
    GitHub Branch
        ↓
    Commit
        ↓
    Pull Request
    """

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

    reported_file_path = extract_file_path(incident)

    if not reported_file_path:
        print("\n❌ Could not identify the source file.")
        return

    print(f"\n📄 Reported file: {reported_file_path}")

    # ---------------------------------------------------------
    # RESOLVE PRODUCTION PATH → LOCAL WORKSPACE
    # ---------------------------------------------------------

    file_path = resolve_repository_path(reported_file_path)

    print(f"📂 Resolved local file: {file_path}")

    if not Path(file_path).exists():
        print(
            f"\n❌ File not found after path resolution: "
            f"{file_path}"
        )
        return

    # ---------------------------------------------------------
    # READ ORIGINAL SOURCE
    # ---------------------------------------------------------

    source_code = read_file(file_path)

    # Keep an immutable copy for retry/revision logic.
    original_source_code = source_code

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
- Do not escape Python quotes with backslashes.
- The PATCH must be valid Python syntax.

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
                print(
                    "\n❌ Revised investigation did not contain a patch."
                )
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
        # TEST FAILURE → RESTORE → INVESTIGATOR
        # -----------------------------------------------------

        print("\n❌ Regression tests failed.")
        print("🔄 Restoring source before retry...\n")

        # Read the currently patched source.
        current_source = read_file(file_path)

        # Restore the source to its state before the failed patch.
        restore_result = apply_file_patch(
            file_path=file_path,
            old_text=current_source,
            new_text=source_code,
        )

        print(f"🔄 Source restore result: {restore_result}")

        if restore_result.startswith("ERROR"):
            print("\n❌ Could not restore source after failed tests.")
            return

        # Make sure the working source is restored.
        source_code = original_source_code

        print("🔄 Sending test failure back to Investigator...\n")

        revision_prompt = f"""
The patch was approved by the QA/Safety Agent,
but the regression tests failed after the patch was applied.

INCIDENT:

{incident}

ORIGINAL SOURCE CODE:

{source_code}

FAILED PATCH:

{patch}

TEST RESULT:

{test_result}

Create a corrected patch that fixes the test failure.

IMPORTANT:
- The source code has been restored to its original state.
- Make the smallest safe production fix.
- Do not introduce fake/default production data.
- Do not use "Default Address", "N/A", or fabricated values.
- Preserve existing functionality.
- Preserve existing business logic.
- Preserve the existing return structure.
- Return the COMPLETE replacement function.
- Do NOT use "# rest of the code".
- Return executable Python code inside PATCH.
- Do not escape Python quotes with backslashes.
- The generated PATCH must be valid Python syntax.

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


# =============================================================
# JIRA INTEGRATION
# =============================================================

def _read_first_log_attachment(jira_data: dict) -> tuple[str, str]:
    """
    Read the first downloaded log/text attachment.

    Returns:
        (filename, log_content)
    """

    downloaded_files = jira_data.get(
        "downloaded_attachments",
        [],
    )

    if not downloaded_files:
        raise RuntimeError(
            "No Jira log attachment was downloaded."
        )

    # Prefer log/text files.
    preferred_files = [
        path
        for path in downloaded_files
        if Path(path).suffix.lower()
        in {".log", ".txt", ".out", ".trace"}
    ]

    if preferred_files:
        file_path = preferred_files[0]
    else:
        file_path = downloaded_files[0]

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Downloaded Jira attachment not found: {file_path}"
        )

    log_content = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    return path.name, log_content


def run_jira_incident_workflow(issue_key: str) -> None:
    """
    Start DevOpsSentinel remediation from a Jira incident.

    Flow:

    Jira
        ↓
    Ticket + attachment
        ↓
    Incident Detector
        ↓
    Existing remediation workflow
        ↓
    Investigator
        ↓
    QA
        ↓
    Tests
        ↓
    GitHub PR
    """

    print("\n========================================")
    print("      DEVOPS SENTINEL + JIRA")
    print("========================================\n")

    # ---------------------------------------------------------
    # JIRA INGESTION
    # ---------------------------------------------------------

    print(
        f"🎫 Fetching Jira incident: {issue_key}\n"
    )

    jira_data = get_jira_incident(issue_key)

    print(
        f"✅ Jira issue retrieved: "
        f"{jira_data.get('key')}"
    )

    print(
        f"📌 Summary: "
        f"{jira_data.get('summary')}"
    )

    print(
        f"📊 Status: "
        f"{jira_data.get('status')}"
    )

    print("\n📄 Jira Description:")
    print(jira_data.get("description", ""))

    # ---------------------------------------------------------
    # LOG ATTACHMENT
    # ---------------------------------------------------------

    print("\n📎 Processing Jira attachment...")

    filename, log_content = _read_first_log_attachment(
        jira_data
    )

    print(
        f"✅ Log attachment loaded: {filename}"
    )

    # ---------------------------------------------------------
    # INCIDENT DETECTOR
    # ---------------------------------------------------------

    print(
        "\n🚨 Incident Detector Agent: "
        "normalizing Jira incident...\n"
    )

    incident = detect_jira_incident(
        description=jira_data.get(
            "description",
            "",
        ),
        log_content=log_content,
        issue_key=jira_data.get(
            "key",
            issue_key,
        ),
    )

    print("\n=== STRUCTURED PRODUCTION INCIDENT ===")
    print(incident)

    # ---------------------------------------------------------
    # EXISTING REMEDIATION WORKFLOW
    # ---------------------------------------------------------

    print(
        "\n🚀 Starting existing "
        "DevOpsSentinel remediation workflow..."
    )

    run_incident_workflow(incident)


# =============================================================
# LOCAL TEST
# =============================================================

if __name__ == "__main__":

    # Jira
    #   ↓
    # Incident Detector
    #   ↓
    # Investigator
    #   ↓
    # QA
    #   ↓
    # Patch
    #   ↓
    # Tests
    #   ↓
    # GitHub PR

    run_jira_incident_workflow("SCRUM-1")