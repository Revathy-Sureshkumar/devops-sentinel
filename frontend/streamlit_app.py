import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.workflows.incident_workflow import run_incident_workflow


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DevOpsSentinel",
    page_icon="🛡️",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ DevOpsSentinel")

st.caption(
    "Autonomous AI Agent for Production Incident Resolution"
)

st.divider()


# ============================================================
# DASHBOARD METRICS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Agent Status",
        "● Online",
    )

with col2:
    st.metric(
        "Active Incident",
        "1",
    )

with col3:
    st.metric(
        "Automation",
        "Enabled",
    )


# ============================================================
# PRODUCTION INCIDENT
# ============================================================

st.subheader("🚨 Production Incident")


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


incident_col, button_col = st.columns([3, 1])


with incident_col:

    st.error(
        """
        **HIGH — payment-service**

        `KeyError: 'billing_address'`

        `demo/sample_repo/app/services/payment.py:3`
        """
    )


with button_col:

    st.write("")
    st.write("")

    run_incident = st.button(
        "🚨 Simulate Incident",
        use_container_width=True,
        type="primary",
    )


# ============================================================
# WORKFLOW
# ============================================================

st.subheader("🔄 Autonomous Remediation Pipeline")

st.write(
    """
    **Detect → Investigate → QA → Patch → Test → GitHub → Human Review**
    """
)


# ============================================================
# RUN WORKFLOW
# ============================================================

if run_incident:

    st.session_state["incident_started"] = True

    st.divider()

    st.subheader("🤖 DevOpsSentinel Agent Activity")

    # --------------------------------------------------------
    # Workflow stages
    # --------------------------------------------------------

    stages = [
        ("🚨", "Incident Detected"),
        ("🔎", "Investigator Agent"),
        ("🛡️", "QA/Safety Agent"),
        ("🛠️", "Patch Application"),
        ("🧪", "Regression Tests"),
        ("🐙", "GitHub Branch"),
        ("📝", "GitHub Commit"),
        ("🔀", "Pull Request"),
        ("👤", "Human Approval"),
    ]

    stage_placeholders = []

    for icon, name in stages:

        placeholder = st.empty()

        placeholder.info(
            f"{icon} **{name}** — Waiting..."
        )

        stage_placeholders.append(
            (placeholder, icon, name)
        )


    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    progress = st.progress(0)

    status = st.empty()


    # --------------------------------------------------------
    # Initial status
    # --------------------------------------------------------

    stage_placeholders[0][0].success(
        "🚨 **Incident Detected** — payment-service reported HIGH severity failure."
    )

    progress.progress(5)

    status.info(
        "🔎 Investigator Agent is analyzing the incident..."
    )


    # --------------------------------------------------------
    # Execute actual workflow
    # --------------------------------------------------------

    output = io.StringIO()

    try:

        with redirect_stdout(output):

            run_incident_workflow(incident)


        workflow_output = output.getvalue()


        # ----------------------------------------------------
        # Determine workflow stages from execution output
        # ----------------------------------------------------

        if "Investigator Agent" in workflow_output:

            stage_placeholders[1][0].success(
                "🔎 **Investigator Agent** — RCA and source inspection completed."
            )

            progress.progress(20)


        if "QA APPROVED PATCH" in workflow_output:

            stage_placeholders[2][0].success(
                "🛡️ **QA/Safety Agent** — Patch approved."
            )

            progress.progress(35)

        elif "QA REVIEW" in workflow_output:

            stage_placeholders[2][0].warning(
                "🛡️ **QA/Safety Agent** — Reviewing proposed remediation."
            )


        if "PATCH APPLIED" in workflow_output:

            stage_placeholders[3][0].success(
                "🛠️ **Patch Application** — Production fix applied."
            )

            progress.progress(50)


        if "TESTS PASSED" in workflow_output:

            stage_placeholders[4][0].success(
                "🧪 **Regression Tests** — All tests passed."
            )

            progress.progress(65)


        if "Branch created:" in workflow_output:

            stage_placeholders[5][0].success(
                "🐙 **GitHub Branch** — Incident branch created."
            )

            progress.progress(75)


        if "Commit:" in workflow_output:

            stage_placeholders[6][0].success(
                "📝 **GitHub Commit** — Remediation committed."
            )

            progress.progress(85)


        if "Pull Request:" in workflow_output:

            stage_placeholders[7][0].success(
                "🔀 **Pull Request** — Automated remediation PR created."
            )

            progress.progress(95)


        if "Human approval required" in workflow_output:

            stage_placeholders[8][0].warning(
                "👤 **Human Approval** — Review required before merge."
            )

            progress.progress(100)

            status.success(
                "✅ Automated remediation completed successfully. "
                "Human approval is required before merge."
            )

        else:

            progress.progress(100)

            status.success(
                "✅ Incident workflow completed."
            )


        # ====================================================
        # EXECUTION LOG
        # ====================================================

        st.divider()

        st.subheader("📋 Agent Execution Log")

        with st.expander(
            "View detailed Investigator / QA / GitHub logs",
            expanded=False,
        ):

            st.code(
                workflow_output,
                language="text",
            )


        # ====================================================
        # GITHUB RESULT
        # ====================================================

        if "Pull Request:" in workflow_output:

            st.divider()

            st.subheader("🔀 Remediation Pull Request")

            pr_url = None

            for line in workflow_output.splitlines():

                if "Pull Request:" in line:

                    possible_url = line.split(
                        "Pull Request:",
                        1
                    )[1].strip()

                    if possible_url.startswith("http"):

                        pr_url = possible_url

                        break


            if pr_url:

                st.success(
                    "✅ Automated remediation PR created successfully."
                )

                st.link_button(
                    "🔀 Review Pull Request",
                    pr_url,
                    use_container_width=True,
                )


    except Exception as exc:

        progress.progress(100)

        status.error(
            "❌ DevOpsSentinel workflow failed."
        )

        st.error(
            f"Error: {exc}"
        )

        with st.expander(
            "View error details"
        ):

            st.exception(exc)


# ============================================================
# ROOT CAUSE
# ============================================================

st.divider()

left, right = st.columns(2)


with left:

    st.subheader("🔍 Root Cause")

    st.info(
        """
        `process_payment()` directly accesses:

        `request["billing_address"]`

        When the required field is missing, the application
        raises a `KeyError`.

        DevOpsSentinel identifies this failure and generates
        a targeted validation fix.
        """
    )


with right:

    st.subheader("🛡️ Agent Architecture")

    st.write(
        """
        **🔎 Investigator Agent**

        Investigates the incident, inspects repository files,
        identifies the root cause, and generates a remediation.

        **🛡️ QA/Safety Agent**

        Independently reviews the proposed patch for correctness,
        regression risk, and operational safety.

        **🐙 GitHub Automation**

        Creates an incident branch, commits the remediation,
        and opens a Pull Request.

        **👤 Human Approval**

        The system never auto-merges. Final approval remains
        with a human engineer.
        """
    )


# ============================================================
# WORKFLOW SUMMARY
# ============================================================

st.divider()

st.subheader("🔄 DevOpsSentinel Workflow")

workflow_cols = st.columns(9)

workflow_items = [
    ("🚨", "Detect"),
    ("🔎", "Investigate"),
    ("🛡️", "QA"),
    ("🛠️", "Fix"),
    ("🧪", "Test"),
    ("🐙", "Branch"),
    ("📝", "Commit"),
    ("🔀", "PR"),
    ("👤", "Approve"),
]

for column, (icon, label) in zip(
    workflow_cols,
    workflow_items,
):

    with column:

        st.markdown(
            f"""
            <div style="text-align:center;">
                <div style="font-size:28px;">{icon}</div>
                <b>{label}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )