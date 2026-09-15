#!/usr/bin/env python3
"""PR gate for the control catalog.

Fails if any control is missing required fields, has an unknown framework,
references an evidence source that has no collector, or is flagged public
while still 'planned'. With --crosswalks, regenerates framework tables.
"""
import sys
import glob
import argparse
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTROLS = ROOT / "trust-center" / "controls"
FRAMEWORKS_DIR = ROOT / "trust-center" / "frameworks"

REQUIRED = ["id", "title", "domain", "owner", "status", "public", "statement", "frameworks", "evidence"]
STATUSES = {"planned", "partial", "implemented", "not-applicable"}
KNOWN_FRAMEWORKS = {
    "soc2", "iso27001_2022", "nist_csf_2", "cis_v8_1",          # commercial
    "nist_800_53_r5", "fedramp_moderate", "stateramp", "txramp",  # federal / state
    "cjis", "ferpa", "hecvat", "nist_800_171", "cmmc",             # sector-specific
    "pci_dss_4", "hipaa",
}
KNOWN_SOURCES = {"okta", "aws_config", "scanner", "edr", "github", "jira", "hris"}


def load_controls():
    controls = []
    for path in sorted(glob.glob(str(CONTROLS / "*.yaml"))):
        with open(path) as f:
            data = yaml.safe_load(f)
        data["_path"] = path
        controls.append(data)
    return controls


def validate(controls):
    errors = []
    seen = set()
    for c in controls:
        name = Path(c["_path"]).name
        for field in REQUIRED:
            if field not in c or c[field] in (None, "", []):
                errors.append(f"{name}: missing required field '{field}'")
        cid = c.get("id")
        if cid in seen:
            errors.append(f"{name}: duplicate id {cid}")
        seen.add(cid)
        if cid and name != f"{cid}.yaml":
            errors.append(f"{name}: filename does not match id {cid}")
        if c.get("status") not in STATUSES:
            errors.append(f"{name}: status must be one of {sorted(STATUSES)}")
        if c.get("public") is True and c.get("status") == "planned":
            errors.append(f"{name}: public controls cannot be 'planned' — plans are not posture")
        for fw in (c.get("frameworks") or {}):
            if fw not in KNOWN_FRAMEWORKS:
                errors.append(f"{name}: unknown framework '{fw}'")
        for ev in (c.get("evidence") or []):
            for k in ("id", "source", "assertion", "freshness_days"):
                if k not in ev:
                    errors.append(f"{name}: evidence entry missing '{k}'")
            if ev.get("source") not in KNOWN_SOURCES:
                errors.append(f"{name}: evidence source '{ev.get('source')}' has no collector")
    return errors


def write_crosswalks(controls):
    FRAMEWORKS_DIR.mkdir(parents=True, exist_ok=True)
    for fw in sorted(KNOWN_FRAMEWORKS):
        table = defaultdict(list)
        for c in controls:
            for crit in (c.get("frameworks") or {}).get(fw, []):
                table[str(crit)].append(c["id"])
        if not table:
            continue  # no controls claim this framework yet — no table
        lines = [f"# {fw} crosswalk", "", "Generated — do not edit by hand.", "",
                 "| Criterion | Controls |", "|---|---|"]
        for crit in sorted(table):
            lines.append(f"| {crit} | {', '.join(sorted(table[crit]))} |")
        (FRAMEWORKS_DIR / f"{fw}.md").write_text("\n".join(lines) + "\n")
        print(f"wrote {fw}.md ({len(table)} criteria)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crosswalks", action="store_true", help="regenerate framework crosswalk tables")
    args = ap.parse_args()

    controls = load_controls()
    if not controls:
        print("no controls found", file=sys.stderr)
        sys.exit(1)
    errors = validate(controls)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    print(f"{len(controls)} controls valid")
    if args.crosswalks:
        write_crosswalks(controls)


if __name__ == "__main__":
    main()
