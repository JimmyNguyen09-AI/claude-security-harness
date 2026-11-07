import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "evals"


def fixture_module(kind):
    spec = importlib.util.spec_from_file_location("owned_fixture_" + kind, ROOT / kind / "invoices.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def objects():
    return ({"id": "u1", "tenant_id": "A", "role": "member", "active": True},
            {"id": "i1", "tenant_id": "A", "owner_id": "u1", "description": "demo"})


@pytest.mark.parametrize("kind", ["vulnerable", "fixed"])
def test_positive_control_owner_can_read(kind):
    user, invoice = objects()
    assert fixture_module(kind).read_invoice(user, invoice)["id"] == "i1"


@pytest.mark.parametrize("mutation", ["cross-tenant", "revoked", "non-owner"])
def test_negative_control_reproduces_only_on_vulnerable_fixture(mutation):
    user, invoice = objects()
    if mutation == "cross-tenant":
        user["tenant_id"] = "B"
    elif mutation == "revoked":
        user["active"] = False
    else:
        user["id"] = "u2"
    assert fixture_module("vulnerable").read_invoice(user, invoice)["id"] == "i1"
    with pytest.raises(PermissionError):
        fixture_module("fixed").read_invoice(user, invoice)


def test_denied_mutation_has_no_side_effect():
    user, invoice = objects()
    original = dict(invoice)
    with pytest.raises(PermissionError):
        fixture_module("fixed").update_invoice(user, invoice, {"tenant_id": "B"})
    assert invoice == original
    fixture_module("vulnerable").update_invoice(user, invoice, {"tenant_id": "B"})
    assert invoice["tenant_id"] == "B"
