import io
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from contextlib import redirect_stdout

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st

from app.workflows.incident_workflow import (
    run_jira_incident_workflow,
)
from app.tools.failure_injector import inject_payment_failure
from app.tools.repository import read_file


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DevOpsSentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM UI
# ============================================================

st.html(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 85% 8%,
                rgba(0, 190, 255, .08),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #07111d 0%,
                #0a1420 52%,
                #060d15 100%
            );
        color: #e8f1f8;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #091521 0%,
            #07101a 100%
        );
        border-right: 1px solid #1b3043;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem;
    }

    .brand {
        font-size: 25px;
        font-weight: 800;
        letter-spacing: -.7px;
    }

    .brand span {
        color: #16c7ff;
    }

    .side-subtitle {
        color: #7f95a8;
        font-size: 12px;
        margin-top: 3px;
        margin-bottom: 24px;
    }

    .section-label {
        color: #7e93a6;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin: 20px 0 9px;
    }

    .agent {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 9px 0;
        border-bottom: 1px solid rgba(130,160,185,.08);
    }

    .agent-name {
        font-size: 12px;
        font-weight: 700;
    }

    .agent-desc {
        color: #708699;
        font-size: 10px;
        margin-top: 2px;
    }

    .pill {
        color: #00e39a;
        background: rgba(0,227,154,.10);
        border: 1px solid rgba(0,227,154,.22);
        border-radius: 999px;
        padding: 4px 8px;
        font-size: 9px;
        font-weight: 800;
    }

    .repo {
        padding: 8px 0;
        font-size: 12px;
    }

    .ok {
        float: right;
        color: #00df9a;
        font-weight: 800;
        font-size: 10px;
    }

    .bad {
        float: right;
        color: #ff626b;
        font-weight: 800;
        font-size: 10px;
    }

    .online {
        display: inline-block;
        float: right;
        color: #00e39a;
        border: 1px solid rgba(0,227,154,.25);
        background: rgba(0,227,154,.07);
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 11px;
        font-weight: 800;
        margin-top: 8px;
    }

    .metric {
        background: linear-gradient(
            145deg,
            rgba(17,33,49,.96),
            rgba(9,21,33,.96)
        );
        border: 1px solid #20384d;
        border-radius: 10px;
        padding: 15px 16px;
        min-height: 96px;
    }

    .metric-label {
        color: #8da2b4;
        font-size: 11px;
        font-weight: 700;
    }

    .metric-value {
        font-size: 27px;
        font-weight: 850;
        margin-top: 8px;
    }

    .red {
        color: #ff5c65;
    }

    .cyan {
        color: #42ceff;
    }

    .green {
        color: #3ce69f;
    }

    .light {
        color: #a9c9e2;
    }

    .incident {
        background: linear-gradient(
            145deg,
            rgba(69,17,26,.72),
            rgba(17,20,29,.96)
        );
        border: 1px solid rgba(255,82,92,.48);
        border-radius: 10px;
        padding: 18px 20px;
    }

    .incident-title {
        font-size: 19px;
        font-weight: 800;
    }

    .critical {
        color: #ff626b;
        font-weight: 850;
        font-size: 13px;
    }

    .meta {
        color: #91a6b7;
        font-size: 11px;
        margin-top: 5px;
    }

    .summary {
        color: #d4dee7;
        font-size: 13px;
        margin-top: 14px;
    }

    .panel {
        background: linear-gradient(
            145deg,
            rgba(15,30,45,.97),
            rgba(8,19,30,.97)
        );
        border: 1px solid #20384d;
        border-radius: 10px;
        padding: 14px;
        margin-top: 14px;
    }

    .panel-title {
        color: #b9cad8;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: .6px;
        margin-bottom: 9px;
    }

    .timeline-item {
        position: relative;
        padding: 7px 0 9px 23px;
        border-left: 2px solid #263e54;
        margin-left: 8px;
    }

    .timeline-item:last-child {
        border-left-color: transparent;
    }

    .dot {
        position: absolute;
        left: -7px;
        top: 10px;
        width: 11px;
        height: 11px;
        border-radius: 50%;
        background: #162b40;
        border: 2px solid #526d86;
    }

    .dot.active {
        background: #16c7ff;
        border-color: #72e4ff;
        box-shadow: 0 0 13px rgba(22,199,255,.55);
    }

    .dot.done {
        background: #00d996;
        border-color: #61efbd;
        box-shadow: 0 0 11px rgba(0,217,150,.35);
    }

    .timeline-title {
        font-size: 12px;
        font-weight: 750;
    }

    .timeline-desc {
        color: #70869a;
        font-size: 10px;
        margin-top: 2px;
    }

    .info-card {
        background: linear-gradient(
            145deg,
            rgba(15,30,45,.97),
            rgba(8,19,30,.97)
        );
        border: 1px solid #20384d;
        border-radius: 10px;
        padding: 15px;
        min-height: 145px;
    }

    .info-title {
        font-size: 13px;
        font-weight: 800;
        margin-bottom: 9px;
    }

    .info-text {
        color: #9db0bf;
        font-size: 11px;
        line-height: 1.65;
    }

    div.stButton > button[kind="primary"] {
        min-height: 56px;
        border-radius: 9px;
        font-size: 14px;
        font-weight: 800;
        background: linear-gradient(
            135deg,
            #0ea5ff,
            #0878ff
        );
        border: 1px solid #2ac8ff;
        box-shadow: 0 0 25px rgba(14,165,255,.18);
    }

    div.stButton > button[kind="primary"]:hover {
        border-color: #7be5ff;
        box-shadow: 0 0 30px rgba(14,165,255,.32);
    }

    .note {
        color: #71879a;
        font-size: 10px;
        line-height: 1.5;
        margin-top: 8px;
    }

    </style>
    """,
)


# ============================================================
# CONSTANTS
# ============================================================

PAYMENT_FILE = (
    "demo/sample_repo/app/services/payment.py"
)



# ============================================================
# SESSION STATE
# ============================================================

if "incident" not in st.session_state:
    st.session_state["incident"] = None

if "workflow_success" not in st.session_state:
    st.session_state["workflow_success"] = False

if "workflow_duration" not in st.session_state:
    st.session_state["workflow_duration"] = None

if "pr_url" not in st.session_state:
    st.session_state["pr_url"] = None

if "before_code" not in st.session_state:
    st.session_state["before_code"] = None

if "after_code" not in st.session_state:
    st.session_state["after_code"] = None

if "workflow_output" not in st.session_state:
    st.session_state["workflow_output"] = ""

if "completed_stages" not in st.session_state:
    st.session_state["completed_stages"] = set()

if "jira_url" not in st.session_state:
    st.session_state["jira_url"] = ""

if "jira_issue_key" not in st.session_state:
    st.session_state["jira_issue_key"] = None


# ============================================================
# HELPERS
# ============================================================

def read_payment():
    try:
        return read_file(PAYMENT_FILE)
    except Exception as exc:
        return f"Unable to read {PAYMENT_FILE}: {exc}"


def extract_jira_issue_key(jira_url: str) -> str:
    """Extract and validate a Jira issue key from a Jira browse URL."""

    jira_url = jira_url.strip()

    if not jira_url:
        raise ValueError("Please enter a JIRA incident URL.")

    parsed = urlparse(jira_url)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(
            "Invalid JIRA URL. Expected format: "
            "https://your-domain.atlassian.net/browse/PROJECT-123"
        )

    path = parsed.path.rstrip("/")

    if "/browse/" not in path:
        raise ValueError(
            "Invalid JIRA URL. Expected a Jira browse URL, for example: "
            "https://your-domain.atlassian.net/browse/SCRUM-1"
        )

    issue_key = path.split("/browse/", 1)[1].split("/", 1)[0].strip()

    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*-\d+", issue_key):
        raise ValueError(
            f"Invalid JIRA issue key: {issue_key or 'missing'}. "
            "Expected something like SCRUM-1."
        )

    return issue_key.upper()

def incident_field(text, field):
    prefix = field.lower() + ":"

    for line in text.splitlines():

        if line.strip().lower().startswith(prefix):

            return line.split(
                ":",
                1,
            )[1].strip()

    return "Not available"


def metric(label, value, css):

    st.html(
        f"""
        <div class="metric">

            <div class="metric-label">
                {label}
            </div>

            <div class="metric-value {css}">
                {value}
            </div>

        </div>
        """
    )


def extract_incident_from_workflow(workflow_output: str) -> str | None:
    """Extract the structured Incident Detector result from workflow output."""

    match = re.search(
        r"(PRODUCTION INCIDENT\s+.*?)(?=\n(?:ROOT CAUSE:|===|---)|\Z)",
        workflow_output,
        re.DOTALL | re.IGNORECASE,
    )

    if not match:
        return None

    return match.group(1).strip()




# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html(
        """
        <div class="brand">
            🛡️ DevOps<span>Sentinel</span>
        </div>
        """
    )

    st.html(
        """
        <div class="side-subtitle">
            Autonomous Production Reliability
        </div>
        """
    )

    st.html(
        '<div class="section-label">AI Agents</div>'
    )

    agents = [
        (
            "🤖",
            "Incident Detector",
            "Bedrock Analysis",
        ),
        (
            "🔎",
            "Investigator Agent",
            "RCA & Code Analysis",
        ),
        (
            "🛡️",
            "QA/Safety Agent",
            "Patch Review",
        ),
        (
            "✓",
            "Deployment Guard",
            "Human-in-the-Loop",
        ),
    ]

    for icon, name, desc in agents:

        st.html(
            f"""
            <div class="agent">

                <div>

                    <div class="agent-name">
                        {icon} {name}
                    </div>

                    <div class="agent-desc">
                        {desc}
                    </div>

                </div>

                <span class="pill">
                    Ready
                </span>

            </div>
            """
        )

    st.html(
        '<div class="section-label">Repository</div>'
    )

    st.html(
        """
        <div class="repo">
            🐙 <b>devops-sentinel</b>
            <span class="ok">ONLINE</span>
        </div>

        <div class="repo">
            📁 payment-service
            <span class="bad">INCIDENT</span>
        </div>

        <div class="repo">
            📁 frontend-app
            <span class="ok">HEALTHY</span>
        </div>

        <div class="repo">
            📁 api-gateway
            <span class="ok">HEALTHY</span>
        </div>
        """
    )

    st.html(
        '<div class="section-label">Demo Environment</div>'
    )

    st.html(
        """
        <div class="note">
            Controlled failure injection is enabled.
            The known buggy payment fixture is copied into
            the sample repository before each resolution run.
        </div>
        """
    )



# ============================================================
# HEADER
# ============================================================

head_left, head_right = st.columns(
    [5, 1]
)

with head_left:

    st.title(
        "DevOpsSentinel"
    )

    st.caption(
        "Autonomous AI Agent for Production Incident Resolution"
    )

with head_right:

    st.html(
        """
        <div class="online">
            ● Agent Online
        </div>
        """
    )


# ============================================================
# METRICS
# ============================================================

# Show operational metrics only after a JIRA workflow has run.
if st.session_state["workflow_output"]:

    m1, m2, m3, m4 = st.columns(4)

    workflow_output = st.session_state["workflow_output"]

    with m1:
        if st.session_state["workflow_success"]:
            active_incidents = "0 Resolved"
            active_css = "green"
        else:
            active_incidents = "1 Active"
            active_css = "red"

        metric("Active Incidents", active_incidents, active_css)

    with m2:
        if st.session_state["workflow_duration"] is not None:
            duration = f"{st.session_state['workflow_duration']:.1f}s"
        else:
            duration = "—"

        metric("Last MTTR", duration, "cyan")

    with m3:
        if "ROOT CAUSE:" in workflow_output and "TESTS PASSED" in workflow_output:
            rca_status = "Verified"
        elif "ROOT CAUSE:" in workflow_output:
            rca_status = "Analyzed"
        else:
            rca_status = "Failed"

        metric("RCA Status", rca_status, "green")

    with m4:
        pr_status = "1 Created" if st.session_state["pr_url"] else "0"
        metric("PRs Created", pr_status, "light")

    st.write("")


# INCIDENT AREA
# ============================================================

st.subheader("🎫 JIRA Incident Source")

jira_url = st.text_input(
    "JIRA Incident URL",
    value=st.session_state["jira_url"],
    placeholder="https://your-domain.atlassian.net/browse/PROJECT-123",
    help=(
        "Paste the JIRA incident URL. DevOpsSentinel will "
        "extract the issue key, fetch the ticket and its "
        "production telemetry, and start remediation."
    ),
)

if jira_url != st.session_state["jira_url"]:

    st.session_state["jira_url"] = jira_url

    # New JIRA URL starts a fresh incident context.
    st.session_state["incident"] = None
    st.session_state["workflow_success"] = False
    st.session_state["workflow_duration"] = None
    st.session_state["pr_url"] = None
    st.session_state["before_code"] = None
    st.session_state["after_code"] = None
    st.session_state["workflow_output"] = ""
    st.session_state["completed_stages"] = set()
    st.session_state["jira_issue_key"] = None


validated_issue_key = None

if jira_url.strip():

    try:
        validated_issue_key = extract_jira_issue_key(jira_url)
        st.session_state["jira_issue_key"] = validated_issue_key

        st.success(
            f"✓ JIRA issue detected: **{validated_issue_key}**"
        )

    except ValueError as exc:
        st.error(str(exc))

else:
    st.caption(
        "Enter a JIRA incident URL to begin autonomous incident analysis."
    )


# ============================================================
# INCIDENT DISPLAY
# ============================================================

incident = st.session_state["incident"]

if incident:

    service = incident_field(incident, "Service")
    severity = incident_field(incident, "Severity")
    timestamp = incident_field(incident, "Timestamp")
    environment = incident_field(incident, "Environment")

    error_match = re.search(
        r"Error:\s*(.*?)(?=\n\n|\nLocation:)",
        incident,
        re.DOTALL | re.IGNORECASE,
    )

    error_text = (
        error_match.group(1).strip()
        if error_match
        else "Production incident detected"
    )

    summary_match = re.search(
        r"Incident Summary:\s*(.*?)(?:\n\n|\Z)",
        incident,
        re.DOTALL | re.IGNORECASE,
    )

    summary_text = (
        summary_match.group(1).strip()
        if summary_match
        else "Production incident detected from JIRA telemetry."
    )

    st.html(
        f"""
        <div class="incident">
            <div>
                <span class="critical">
                    🚨 {severity.upper()}:
                </span>

                <span class="incident-title">
                    {error_text}
                </span>
            </div>

            <div class="meta">
                {service}
                &nbsp;|&nbsp;
                {environment}
                &nbsp;|&nbsp;
                {severity}
                &nbsp;|&nbsp;
                {timestamp}
            </div>

            <div class="summary">
                {summary_text}
            </div>
        </div>
        """
    )

    st.html(
        """
        <div class="panel">
            <div class="panel-title">
                PRODUCTION INCIDENT
            </div>
        </div>
        """
    )

    st.code(incident, language="text")

elif not jira_url.strip():

    st.info(
        "Enter a JIRA incident URL above to begin analysis."
    )

elif validated_issue_key is not None:

    st.caption(
        "JIRA is ready. Click **Resolve Incident** to start the autonomous analysis."
    )


# ============================================================
# RESOLVE INCIDENT
# ============================================================

action_col = st.columns([1.15])[0]

with action_col:

    run_incident = st.button(
        "🚨 Resolve Incident",
        use_container_width=True,
        type="primary",
    )

    st.html(
        """
        <div class="note">
            Start autonomous remediation pipeline
        </div>
        """
    )


# REMEDIATION WORKFLOW
# ============================================================

if run_incident:

    try:
        issue_key = extract_jira_issue_key(jira_url)
        st.session_state["jira_issue_key"] = issue_key

    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    start_time = time.time()

    # --------------------------------------------------------
    # # RESET DEMO FAILURE
    # --------------------------------------------------------

    try:

        inject_payment_failure()

    except Exception as exc:

        st.error(
            "❌ Failed to inject demo incident."
        )

        st.exception(exc)

        st.stop()


    # Capture buggy source before remediation.

    st.session_state[
        "before_code"
    ] = read_payment()

    st.session_state[
        "after_code"
    ] = None

    st.session_state[
        "pr_url"
    ] = None

    st.session_state[
        "workflow_success"
    ] = False

    st.session_state[
        "completed_stages"
    ] = {0}


    # --------------------------------------------------------
    # USE JIRA AS REAL INCIDENT SOURCE
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🎫 Jira Incident"
    )

    st.info(
        f"DevOpsSentinel will ingest JIRA {issue_key} "
        "and its production log attachment."
    )


    # --------------------------------------------------------
    # RUN JIRA WORKFLOW
    # --------------------------------------------------------

    st.subheader(
        "🤖 Autonomous Agent Activity"
    )

    progress = st.progress(5)

    status = st.empty()

    output = io.StringIO()


    try:

        status.info(
            f"🎫 Fetching Jira incident {issue_key}..."
        )

        progress.progress(10)

        with redirect_stdout(output):

            run_jira_incident_workflow(
                issue_key
            )

        workflow_output = output.getvalue()

        st.session_state[
            "workflow_output"
        ] = workflow_output

        detected_incident = extract_incident_from_workflow(
            workflow_output
        )

        if detected_incident:
            st.session_state["incident"] = detected_incident

        # Use the Incident Detector result generated from the
        # submitted JIRA ticket, not a hardcoded production log.
        detected_incident = extract_incident_from_workflow(
            workflow_output
        )

        if detected_incident:
            st.session_state["incident"] = detected_incident


        # ----------------------------------------------------
        # DETERMINE COMPLETED STAGES
        # ----------------------------------------------------

        completed = {0}


        if "Incident Detector Agent" in workflow_output:

            completed.add(1)

            progress.progress(20)

            status.info(
                "🚨 Incident Detector normalized production telemetry"
            )


        if "Investigator Agent" in workflow_output:

            completed.add(2)

            progress.progress(35)

            status.info(
                "🔎 Investigator completed root-cause analysis"
            )


        if "QA APPROVED PATCH" in workflow_output:

            completed.add(3)

            progress.progress(50)

            status.success(
                "🛡️ QA/Safety Agent approved the remediation"
            )

        elif "QA REVIEW" in workflow_output:

            completed.add(3)


        if "PATCH APPLIED" in workflow_output:

            completed.add(4)

            progress.progress(60)

            status.info(
                "🔧 Remediation patch applied"
            )


        if "TESTS PASSED" in workflow_output:

            completed.add(5)

            progress.progress(72)

            status.success(
                "🧪 Regression tests passed"
            )


        if "Branch created:" in workflow_output:

            completed.add(6)

            progress.progress(82)

            status.info(
                "🐙 GitHub incident branch created"
            )


        if "Commit:" in workflow_output:

            completed.add(7)

            progress.progress(90)

            status.info(
                "📝 Remediation commit created"
            )


        if "Pull Request:" in workflow_output:

            completed.add(8)

            progress.progress(95)

            status.info(
                "🔀 GitHub Pull Request created"
            )


        if "Human approval required" in workflow_output:

            completed.add(9)


        st.session_state[
            "completed_stages"
        ] = completed


        # ----------------------------------------------------
        # READ FINAL SOURCE
        # ----------------------------------------------------

        st.session_state[
            "after_code"
        ] = read_payment()


        # ----------------------------------------------------
        # FIND PR URL
        # ----------------------------------------------------

        pr_url = None

        for line in workflow_output.splitlines():

            if "Pull Request:" in line:

                candidate = line.split(
                    "Pull Request:",
                    1,
                )[1].strip()

                if candidate.startswith("http"):

                    pr_url = candidate

                    break


        if pr_url:

            st.session_state[
                "pr_url"
            ] = pr_url


        # ----------------------------------------------------
        # WORKFLOW DURATION
        # ----------------------------------------------------

        duration = (
            time.time() - start_time
        )

        st.session_state[
            "workflow_duration"
        ] = duration


        # ----------------------------------------------------
        # FINAL STATUS
        # ----------------------------------------------------

        if "TESTS PASSED" in workflow_output:

            st.session_state[
                "workflow_success"
            ] = True

            progress.progress(100)

            if "Human approval required" in workflow_output:

                status.success(
                    "✅ Remediation completed successfully. "
                    "Human approval is required before merge."
                )

            else:

                status.success(
                    "✅ Incident workflow completed successfully."
                )

        else:

            progress.progress(100)

            status.warning(
                "⚠️ Workflow completed, but regression tests "
                "did not report success."
            )


        # ----------------------------------------------------
        # EXECUTION LOG
        # ----------------------------------------------------

        st.html(
            """
            <div class="panel">

                <div class="panel-title">
                    EXECUTION LOG
                </div>

            </div>
            """
        )

        with st.expander(
            "View Investigator / QA / GitHub logs",
            expanded=False,
        ):

            st.code(
                workflow_output,
                language="text",
            )


        # ----------------------------------------------------
        # RESULT SUMMARY
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "📊 Remediation Summary"
        )

        r1, r2, r3, r4 = st.columns(4)

        with r1:

            if "Incident Detector Agent" in workflow_output:

                st.success(
                    "🚨 Incident Detected"
                )

            else:

                st.warning(
                    "Incident Detection"
                )


        with r2:

            if "QA APPROVED PATCH" in workflow_output:

                st.success(
                    "🛡️ QA Approved"
                )

            else:

                st.warning(
                    "QA Review"
                )


        with r3:

            if "TESTS PASSED" in workflow_output:

                st.success(
                    "🧪 Tests Passed"
                )

            else:

                st.error(
                    "Tests Failed"
                )


        with r4:

            if pr_url:

                st.success(
                    "🔀 PR Created"
                )

            else:

                st.warning(
                    "No PR"
                )


        # ----------------------------------------------------
        # ROOT CAUSE
        # ----------------------------------------------------

        st.subheader(
            "🔎 Root Cause"
        )

        root_cause_match = re.search(
            r"ROOT CAUSE:\s*(.*?)(?=\n\n|\nIMPACT:)",
            workflow_output,
            re.DOTALL | re.IGNORECASE,
        )

        if root_cause_match:

            st.info(
                root_cause_match.group(1).strip()
            )

        else:

            st.info(
                "The Investigator identified the root cause "
                "from the production incident telemetry."
            )


        # ----------------------------------------------------
        # PATCH
        # ----------------------------------------------------

        st.subheader(
            "🔧 Generated Remediation"
        )

        patch_match = re.search(
            r"PATCH:\s*(.*?)(?=\nASSUMPTIONS:|\Z)",
            workflow_output,
            re.DOTALL | re.IGNORECASE,
        )

        if patch_match:

            patch_text = patch_match.group(1).strip()

            st.code(
                patch_text,
                language="python",
            )


        # ----------------------------------------------------
        # BEFORE / AFTER
        # ----------------------------------------------------

        before_col, after_col = st.columns(2)

        with before_col:

            st.subheader(
                "❌ Before"
            )

            if st.session_state["before_code"]:

                st.code(
                    st.session_state["before_code"],
                    language="python",
                )


        with after_col:

            st.subheader(
                "✅ After"
            )

            if st.session_state["after_code"]:

                st.code(
                    st.session_state["after_code"],
                    language="python",
                )


        # ----------------------------------------------------
        # GITHUB
        # ----------------------------------------------------

        st.subheader(
            "🐙 GitHub Remediation"
        )

        if pr_url:

            st.success(
                "Automated remediation Pull Request created."
            )

            st.link_button(
                "🔀 Review Pull Request",
                pr_url,
                use_container_width=True,
            )

        else:

            st.warning(
                "GitHub Pull Request was not created."
            )


        # ----------------------------------------------------
        # HUMAN APPROVAL
        # ----------------------------------------------------

        if "Human approval required" in workflow_output:

            st.markdown(
                """
                <div class="success-card">

                <h3>👤 Human Approval Required</h3>

                DevOpsSentinel completed the automated
                remediation successfully.

                <br><br>

                The system <b>does not automatically merge</b>
                the Pull Request.

                <br><br>

                Review the generated code and approve the
                GitHub Pull Request manually.

                </div>
                """,
                unsafe_allow_html=True,
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

            if output.getvalue():

                st.code(
                    output.getvalue(),
                    language="text",
                )


# ============================================================
# EXISTING WORKFLOW RESULT
# ============================================================

elif st.session_state["workflow_output"]:

    workflow_output = (
        st.session_state["workflow_output"]
    )

    st.divider()

    st.subheader(
        "📊 Last Remediation"
    )

    if st.session_state["workflow_success"]:

        st.success(
            "🎉 Last incident was successfully remediated."
        )

    if st.session_state["pr_url"]:

        st.link_button(
            "🔀 Review GitHub Pull Request",
            st.session_state["pr_url"],
            use_container_width=True,
        )


