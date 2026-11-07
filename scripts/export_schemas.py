import json
from pathlib import Path

from security_harness.models import AuthMatrix, Policy, Review, TestSpec, Verification

root = Path(__file__).resolve().parents[1] / "schemas"
root.mkdir(exist_ok=True)
for name, model in {"review": Review, "verification": Verification, "policy": Policy,
                    "test": TestSpec, "auth-matrix": AuthMatrix}.items():
    (root / f"{name}.schema.json").write_text(
        json.dumps(model.model_json_schema(), indent=2) + "\n", encoding="utf-8")
