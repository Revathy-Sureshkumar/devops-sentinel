from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def list_files() -> str:
    """
    List source files in the project repository.
    """
    files = []

    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue

        # Ignore virtual environment and cache files
        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue

        files.append(str(path.relative_to(PROJECT_ROOT)))

    return "\n".join(sorted(files))


def read_file(file_path: str) -> str:
    """
    Read the contents of a file from the project repository.
    """
    requested = (PROJECT_ROOT / file_path).resolve()

    # Prevent path traversal outside the project
    if PROJECT_ROOT not in requested.parents and requested != PROJECT_ROOT:
        return "ERROR: Access outside the project repository is not allowed."

    if not requested.exists():
        return f"ERROR: File not found: {file_path}"

    if not requested.is_file():
        return f"ERROR: Not a file: {file_path}"

    try:
        return requested.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"ERROR: Cannot read {file_path} as UTF-8 text."


def search_code(query: str) -> str:
    """
    Search for a text string across source files in the repository.
    """
    if not query.strip():
        return "ERROR: Search query cannot be empty."

    matches = []

    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue

        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            if query.lower() in line.lower():
                relative_path = path.relative_to(PROJECT_ROOT)
                matches.append(
                    f"{relative_path}:{line_number}: {line.strip()}"
                )

    return "\n".join(matches) if matches else "No matches found."