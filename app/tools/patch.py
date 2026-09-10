from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def apply_file_patch(file_path: str, old_text: str, new_text: str) -> str:
    """Safely replace one exact code block in a repository file."""
    target = (PROJECT_ROOT / file_path).resolve()

    if PROJECT_ROOT not in target.parents:
        return "ERROR: Access outside repository is not allowed."

    if not target.exists():
        return f"ERROR: File not found: {file_path}"

    content = target.read_text(encoding="utf-8")
    count = content.count(old_text)

    if count == 0:
        return "ERROR: Original code block was not found."

    if count > 1:
        return "ERROR: Original code block occurs multiple times."

    target.write_text(
        content.replace(old_text, new_text),
        encoding="utf-8",
    )

    return f"PATCH APPLIED: {file_path}"


def run_tests() -> str:
    """Run the project's pytest test suite."""
    result = subprocess.run(
        ["python", "-m", "pytest", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    output = (result.stdout + "\n" + result.stderr).strip()

    if result.returncode == 0:
        return f"TESTS PASSED\n{output}"

    return f"TESTS FAILED\n{output}"