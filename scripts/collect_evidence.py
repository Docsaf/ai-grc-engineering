#!/usr/bin/env python3
"""Evidence collector skeleton.

Each source is a function returning a dict of metrics. Replace the stubs with
real, read-only API calls (Okta, AWS Config, your scanner, etc.). Every record
written here has the same shape so the scorer and the site never care where
the evidence came from.

Run in CI with OIDC-federated, read-only credentials. Never commit raw API
responses here — push those to write-once object storage and reference them
via raw_ref.
"""
import glob
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTROLS = ROOT / "trust-center" / "controls"
EVIDENCE = ROOT / "trust-center" / "evidence"


# ---- sources -------------------------------------------------------------
# Replace these stubs. Keep the signature: () -> dict of metrics.

def source_okta():
    # e.g. GET /api/v1/users + /api/v1/policies — compute enforced MFA share
    return {"mfa_enforced_pct": 99.6, "total_users": 412, "exceptions": 2}


def source_aws_config():
    # e.g. AWS Config rule compliance for *-encryption-enabled rules
    return {"unencrypted_resources": 0, "resources_evaluated": 1873}


def source_scanner():
    # e.g. open criticals older than SLA from your vulnerability platform
    return {"critical_over_sla": 0, "high_over_sla": 3, "open_critical": 2}


SOURCES = {
    "okta": source_okta,
    "aws_config": source_aws_config,
    "scanner": source_scanner,
}

# ---- collection ----------------------------------------------------------


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    written = 0
    for path in sorted(glob.glob(str(CONTROLS / "*.yaml"))):
        control = yaml.safe_load(open(path))
        for ev in control.get("evidence", []):
            fn = SOURCES.get(ev["source"])
            if fn is None:
                print(f"skip {ev['id']}: no collector for source '{ev['source']}'")
                continue
            metrics = fn()
            payload = json.dumps(metrics, sort_keys=True).encode()
            record = {
                "evidence_id": ev["id"],
                "control_ids": [control["id"]],
                "collected_at": now,
                "source": ev["source"],
                "metrics": metrics,
                "raw_ref": f"s3://grc-evidence/{ev['source']}/{now[:10]}/{ev['id']}.json",
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
            out = EVIDENCE / f"{ev['id']}.json"
            out.write_text(json.dumps(record, indent=2) + "\n")
            written += 1
    print(f"wrote {written} evidence records to {EVIDENCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
