import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")


if not JIRA_BASE_URL:
    raise ValueError("JIRA_BASE_URL is not set in .env")

if not JIRA_EMAIL:
    raise ValueError("JIRA_EMAIL is not set in .env")

if not JIRA_API_TOKEN:
    raise ValueError("JIRA_API_TOKEN is not set in .env")


def _jira_request(method: str, url: str, **kwargs):
    """Make an authenticated Jira Cloud API request."""

    headers = kwargs.pop("headers", {})

    headers.setdefault("Accept", "application/json")

    response = requests.request(
        method,
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers=headers,
        timeout=30,
        **kwargs,
    )

    response.raise_for_status()

    return response


def _extract_adf_text(node) -> str:
    """Extract readable text from Jira's Atlassian Document Format."""

    if isinstance(node, dict):
        parts = []

        if node.get("type") == "text":
            parts.append(node.get("text", ""))

        for child in node.get("content", []):
            text = _extract_adf_text(child)

            if text:
                parts.append(text)

        return "\n".join(parts)

    if isinstance(node, list):
        return "\n".join(
            text
            for item in node
            if (text := _extract_adf_text(item))
        )

    return ""


def get_jira_issue(issue_key: str) -> dict:
    """
    Retrieve a Jira issue including description and attachments.
    """

    url = (
        f"{JIRA_BASE_URL.rstrip('/')}"
        f"/rest/api/3/issue/{issue_key}"
    )

    response = _jira_request(
        "GET",
        url,
        params={
            "fields": (
                "summary,"
                "description,"
                "attachment,"
                "priority,"
                "status,"
                "labels"
            )
        },
    )

    data = response.json()
    fields = data.get("fields", {})

    description = _extract_adf_text(
        fields.get("description", {})
    )

    attachments = []

    for attachment in fields.get("attachment", []) or []:
        attachments.append(
            {
                "filename": attachment.get("filename"),
                "size": attachment.get("size"),
                "mime_type": attachment.get("mimeType"),
                "content_url": attachment.get("content"),
            }
        )

    priority = fields.get("priority")
    status = fields.get("status")

    return {
        "key": data.get("key", issue_key),
        "summary": fields.get("summary", ""),
        "description": description,
        "priority": (
            priority.get("name")
            if priority
            else None
        ),
        "status": (
            status.get("name")
            if status
            else None
        ),
        "labels": fields.get("labels", []),
        "attachments": attachments,
    }


def download_jira_attachment(
    attachment: dict,
    output_dir: str = "demo/logs",
) -> str:
    """
    Download a Jira attachment into demo/logs.

    Returns the downloaded file path.
    """

    filename = attachment.get("filename")
    content_url = attachment.get("content_url")

    if not filename:
        raise ValueError(
            "Jira attachment has no filename"
        )

    if not content_url:
        raise ValueError(
            f"No content URL for attachment: {filename}"
        )

    output_path = Path(output_dir)

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = output_path / filename

    response = _jira_request(
        "GET",
        content_url,
        headers={
            "Accept": "*/*",
        },
        stream=True,
    )

    with open(file_path, "wb") as file:
        for chunk in response.iter_content(
            chunk_size=8192
        ):
            if chunk:
                file.write(chunk)

    return str(file_path)


def get_jira_incident(issue_key: str) -> dict:
    """
    Retrieve a Jira incident and download its log attachments.
    """

    issue = get_jira_issue(issue_key)

    downloaded_files = []

    for attachment in issue.get(
        "attachments",
        []
    ):
        try:
            path = download_jira_attachment(
                attachment
            )

            downloaded_files.append(path)

            print(
                f"Downloaded Jira attachment: {path}"
            )

        except Exception as exc:
            print(
                f"Warning: Could not download "
                f"{attachment.get('filename')}: {exc}"
            )

    return {
        **issue,
        "downloaded_attachments": downloaded_files,
    }