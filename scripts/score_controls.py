#!/usr/bin/env python3
"""Score control health from evidence.

Healthy  — evidence within freshness window and assertion passes
Degraded — assertion fails, or evidence stale by < 2x the window
Failed   — no evidence, or stale by >= 2x the window

Exit code 1 if any public control is Failed, so the site render step can be
gated on it. Assertions are simple comparisons over metric names, e.g.
"mfa_enforced_pct >= 99". No eval() — parsed explicitly.
"""
import glob
import json
import re
import sys
import operator
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTROLS = ROOT / "trust-center" / "controls"
EVIDENCE = ROOT / "trust-center" / "evidence"

OPS = {">=": operator.ge, "<=": operator.le, "==": operator.eq, "!=": operator.ne,
       ">": operator.gt, "<": operator.lt}
ASSERT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(>=|<=|==|!=|>|<)\s*(-?\d+(?:\.\d+)?)\s*$")


def check(assertion, metrics):
    m = ASSERT_RE.match(assertion)
    if not m:
        raise ValueError(f"unparseable assertion: {assertion!r}")
    name, op, value = m.groups()
    if name not in metrics:
        return False
    return OPS[op](float(metrics[name]), float(value))


def main():
    now = datetime.now(timezone.utc)
    failed_public = 0
    rows = []
    for path in sorted(glob.glob(str(CONTROLS / "*.yaml"))):
        c = yaml.safe_load(open(path))
        worst = "Healthy"
        for ev in c.get("evidence", []):
            rec_path = EVIDENCE / f"{ev['id']}.json"
            if not rec_path.exists():
                state = "Failed"
            else:
                rec = json.loads(rec_path.read_text())
                collected = datetime.fromisoformat(rec["collected_at"].replace("Z", "+00:00"))
                age_days = (now - collected).total_seconds() / 86400
                window = float(ev["freshness_days"])
                if age_days >= 2 * window:
                    state = "Failed"
                elif age_days > window or not check(ev["assertion"], rec["metrics"]):
                    state = "Degraded"
                else:
                    state = "Healthy"
            if ["Healthy", "Degraded", "Failed"].index(state) > ["Healthy", "Degraded", "Failed"].index(worst):
                worst = state
        if worst == "Failed" and c.get("public"):
            failed_public += 1
        rows.append((c["id"], c["domain"], worst))

    width = max(len(r[1]) for r in rows)
    for cid, domain, state in rows:
        print(f"{cid:8} {domain:{width}}  {state}")
    print(f"\n{failed_public} public control(s) Failed")
    sys.exit(1 if failed_public else 0)


if __name__ == "__main__":
    main()
