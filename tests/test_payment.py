import importlib.util
from pathlib import Path

import pytest


PAYMENT_FILE = (
    Path(__file__).resolve().parents[1]
    / "demo"
    / "sample_repo"
    / "app"
    / "services"
    / "payment.py"
)


def load_payment_module():
    spec = importlib.util.spec_from_file_location(
        "sample_payment",
        PAYMENT_FILE,
    )

    if spec is None or spec.loader is None:
        raise ImportError("Could not load payment.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


payment = load_payment_module()


def test_payment_with_billing_address():
    request = {
        "amount": 100,
        "billing_address": "Chennai",
    }

    result = payment.process_payment(request)

    assert result["amount"] == 100
    assert result["address"] == "Chennai"


def test_payment_without_billing_address():
    request = {
        "amount": 100,
    }

    with pytest.raises(ValueError, match="billing_address"):
        payment.process_payment(request)