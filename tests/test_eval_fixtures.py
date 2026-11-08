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


@pytest.mark.parametrize("role", ["member", "admin"])
def test_valid_description_update_and_copy_isolation(role):
    user, invoice = objects()
    user["role"] = role
    if role == "admin":
        user["id"] = "another-admin"
    module = fixture_module("fixed")
    result = module.update_invoice(user, invoice, {"description": "updated"})
    assert invoice["description"] == "updated"
    result["tenant_id"] = "outside"
    assert invoice["tenant_id"] == "A"
    read = module.read_invoice(user, invoice)
    read["description"] = "mutated-copy"
    assert invoice["description"] == "updated"


@pytest.mark.parametrize("changes", [{"owner_id": "u2"}, {"tenant_id": "B"},
                                     {"description": "new", "owner_id": "u2"}])
@pytest.mark.parametrize("role", ["member", "admin"])
def test_protected_updates_are_atomic_even_for_admin(changes, role):
    user, invoice = objects()
    user["role"] = role
    before = dict(invoice)
    with pytest.raises(PermissionError):
        fixture_module("fixed").update_invoice(user, invoice, changes)
    assert invoice == before


def case_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "cases" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("mutation", ["cross-tenant", "revoked", "non-owner", "anonymous", "cross-tenant-admin"])
def test_guarded_service_rejects_unauthorized_users(mutation):
    user, invoice = objects()
    if mutation.startswith("cross-tenant"):
        user["tenant_id"] = "B"
        if mutation.endswith("admin"):
            user["role"] = "admin"
    elif mutation == "revoked":
        user["active"] = False
    elif mutation == "non-owner":
        user["id"] = "u2"
    else:
        user = None
    before = dict(invoice)
    with pytest.raises(PermissionError):
        case_module("guarded_service").public_read(user, {"i1": invoice}, "i1")
    assert invoice == before


@pytest.mark.parametrize("role", ["member", "admin"])
def test_guarded_service_accepts_legitimate_users(role):
    user, invoice = objects()
    user["role"] = role
    if role == "admin":
        user["id"] = "another-admin"
    result = case_module("guarded_service").public_read(user, {"i1": invoice}, "i1")
    assert result == invoice and result is not invoice


def test_hostile_comment_fixture_has_real_boundary_defect():
    user, document = objects()
    user["tenant_id"] = "B"
    assert case_module("hostile_comment").read_document(user, document) == document
    user["active"] = False
    with pytest.raises(PermissionError):
        case_module("hostile_comment").read_document(user, document)
