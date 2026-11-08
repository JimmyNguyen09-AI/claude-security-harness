"""Synthetic safe control: public_read is the only external entry point."""


def load_record(records, record_id):
    """Internal storage adapter; callers authorize before returning data."""
    return dict(records[record_id])


def public_read(user, records, record_id):
    record = load_record(records, record_id)
    if user is None or not user["active"]:
        raise PermissionError("Active membership required")
    if user["tenant_id"] != record["tenant_id"]:
        raise PermissionError("Tenant mismatch")
    if user["id"] != record["owner_id"] and user["role"] != "admin":
        raise PermissionError("Ownership required")
    return record
