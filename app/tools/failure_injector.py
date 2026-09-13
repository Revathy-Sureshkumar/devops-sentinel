from pathlib import Path


BUGGY_FILE = Path("demo/fixtures/payment_buggy.py")
TARGET_FILE = Path("demo/sample_repo/app/services/payment.py")


def inject_payment_failure() -> str:
    """Reset the demo payment service to the known buggy state."""

    if not BUGGY_FILE.exists():
        raise FileNotFoundError(
            f"Buggy fixture not found: {BUGGY_FILE}"
        )

    TARGET_FILE.parent.mkdir(parents=True, exist_ok=True)

    TARGET_FILE.write_text(
        BUGGY_FILE.read_text(),
        encoding="utf-8",
    )

    return f"Injected demo failure into {TARGET_FILE}"