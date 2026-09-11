import os
from datetime import datetime

from dotenv import load_dotenv
from github import Github
from github.GithubException import GithubException


load_dotenv()

GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")


def get_github_client() -> Github:
    """Create an authenticated GitHub client."""
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN is not configured."
        )

    return Github(token)


def get_repository():
    """Return the configured GitHub repository."""
    if not GITHUB_OWNER or not GITHUB_REPO:
        raise RuntimeError(
            "GITHUB_OWNER and GITHUB_REPO must be configured."
        )

    github = get_github_client()

    return github.get_repo(
        f"{GITHUB_OWNER}/{GITHUB_REPO}"
    )


def create_incident_branch() -> str:
    """Create a new branch from main."""
    repo = get_repository()

    branch_name = (
        "incident/devops-sentinel-"
        + datetime.now().strftime("%Y%m%d-%H%M%S")
    )

    main_branch = repo.get_branch("main")

    repo.create_git_ref(
        ref=f"refs/heads/{branch_name}",
        sha=main_branch.commit.sha,
    )

    return branch_name


def commit_file(
    branch_name: str,
    file_path: str,
    file_content: str,
    commit_message: str,
) -> str:
    """Create or update a file on the incident branch."""
    repo = get_repository()

    try:
        existing_file = repo.get_contents(
            file_path,
            ref=branch_name,
        )

        result = repo.update_file(
            path=file_path,
            message=commit_message,
            content=file_content,
            sha=existing_file.sha,
            branch=branch_name,
        )

    except GithubException as exc:
        if exc.status != 404:
            raise

        result = repo.create_file(
            path=file_path,
            message=commit_message,
            content=file_content,
            branch=branch_name,
        )

    return result["commit"].html_url


def create_pull_request(
    branch_name: str,
    title: str,
    body: str,
) -> str:
    """Create a pull request from the incident branch to main."""
    repo = get_repository()

    pull_request = repo.create_pull(
        title=title,
        body=body,
        head=branch_name,
        base="main",
    )

    return pull_request.html_url