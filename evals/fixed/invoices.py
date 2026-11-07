"""Synthetic comparison fixture with explicit tenant and ownership rules."""


def authorize(user, invoice):
    if user is None or not user["active"]:
        raise PermissionError("Active session required")
    if user["tenant_id"] != invoice["tenant_id"]:
        raise PermissionError("Tenant mismatch")
    if user["id"] != invoice["owner_id"] and user["role"] != "admin":
        raise PermissionError("Ownership required")


def read_invoice(user, invoice):
    authorize(user, invoice)
    return dict(invoice)


def update_invoice(user, invoice, changes):
    authorize(user, invoice)
    if set(changes) - {"description"}:
        raise PermissionError("Protected field")
    invoice.update(changes)
    return dict(invoice)
