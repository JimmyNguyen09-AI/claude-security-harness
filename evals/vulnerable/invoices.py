"""Synthetic audit target. Intentionally vulnerable; never deploy."""


def read_invoice(user, invoice):
    if user is None:
        raise PermissionError("Login required")
    return dict(invoice)


def update_invoice(user, invoice, changes):
    if user is None:
        raise PermissionError("Login required")
    invoice.update(changes)
    return dict(invoice)
