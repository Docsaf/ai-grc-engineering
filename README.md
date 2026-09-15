# AI GRC Engineering — Building a Trust Center as Code

A sector-neutral handbook and starter kit for building a public **Trust Center** on a **GRC Engineering** pipeline: one control catalog in YAML, evidence collected by scheduled jobs, a static site rendered from both, and questionnaire answers that cite control IDs instead of restating them from memory.

**Read the handbook:** https://docsaf.github.io/ai-grc-engineering/

| Page | What it covers |
|---|---|
| [Handbook landing page](docs/index.md) | Vision, mission, six operating principles, the four-function program structure, and who the Trust Center serves in each sector |
| [Build guide](docs/build-guide.md) | Sector profiles, then phase-by-phase instructions with schemas, CI workflows, operating cadence, and definitions of done |

## Why this exists

Most Trust Centers are marketing pages with a PDF vault behind them. The claims are typed by hand, the evidence lives in someone's screenshots folder, and the questionnaire team rewrites the same answers every week. Buyers can tell.

GRC Engineering treats governance, risk, and compliance as an engineering problem: controls are code, evidence is data, the public page is a build artifact, and every change is a reviewed pull request. This repository shows how to apply that to the one GRC artifact customers actually read.

## Who it is for

The handbook is written for **both private industry and government technology**, because the author has built and run security programs on both sides of that line and the engineering is the same even when the audiences and frameworks are not.

- **Enterprise SaaS vendors** shortening security reviews and keeping SOC 2 / ISO 27001 evidence current between audits.
- **GovTech vendors** selling into federal, state, local, and education markets — showing FedRAMP, StateRAMP, and TX-RAMP status honestly, publishing CJIS and FERPA positions, and writing for eventual public-records exposure.
- **Public agencies, municipalities, and school districts** demonstrating stewardship of resident and student data to boards, councils, parents, auditors, and insurers.
- **Federal programs and contractors** feeding the SSP, POA&M, and continuous-monitoring deliverables from the same catalog and evidence store the public narrative uses, so the ATO package and the Trust Center never diverge.

Nothing here is tied to any one employer, product, or vendor. The examples are generic; the frameworks are the public ones.

## About the author

Dr. Safiatu "Safi" Mojidi has spent 15+ years securing systems across the public and private sectors: Base Information Security Manager for the U.S. Air Force and Space Force with responsibility for 250+ critical space systems; director of a NASA security program; security support to Slack and Salesforce through the Slack acquisition; cyber-risk leadership across the K-12 sector; ransomware recovery and incident-response framework rebuilds for state and local government; and SOC 2 delivered through automation in healthcare. He holds a D.Sc. in Cybersecurity, teaches corporate, network, and cloud security as an adjunct professor, serves on the ISC2 Global DEI Advisory Board, and is Founder and CEO of [Hacking the Workforce](https://www.hackingtheworkforce.org), a nonprofit building pathways into cybersecurity careers.

That combination — federal authorization packages, hyperscale SaaS due diligence, and under-resourced public-sector programs — is why this handbook refuses to pick a side. A school district and a Fortune 500 SaaS company need the same thing from a Trust Center: claims that trace to controls, and controls that trace to evidence.

## What's in this repository

```text
docs/                    GitHub Pages site (the handbook)
trust-center/controls/   Example control catalog — one YAML file per control, crosswalked to
                         SOC 2, ISO 27001:2022, NIST CSF 2.0, CIS v8.1, and NIST SP 800-53 Rev. 5
trust-center/frameworks/ Generated crosswalk tables (never hand-edited)
trust-center/evidence/   Normalized evidence records written by the collector
scripts/                 validate_controls.py (PR gate), collect_evidence.py, score_controls.py
.github/workflows/       PR validation, scheduled evidence collection, Pages deploy
```

The validator recognizes commercial frameworks (SOC 2, ISO 27001, NIST CSF 2.0, CIS v8.1, PCI DSS 4, HIPAA), federal and state programs (NIST SP 800-53 Rev. 5, FedRAMP Moderate, StateRAMP, TX-RAMP, NIST SP 800-171, CMMC), and sector-specific requirements (CJIS, FERPA, HECVAT). Map a control to whichever ones you claim; the crosswalk tables are generated from those mappings.

## Quick start

```bash
pip install pyyaml
python scripts/validate_controls.py --crosswalks   # PR gate: schema, owners, framework refs; regenerates crosswalks
python scripts/collect_evidence.py                 # writes trust-center/evidence/*.json (stub sources)
python scripts/score_controls.py                   # prints Healthy / Degraded / Failed per control
```

Replace the stub sources in `scripts/collect_evidence.py` with read-only API calls to your identity provider, cloud account, endpoint platform, scanner, and CI system. Keep the evidence bucket write-once. Let the site render from the results.

## Enabling the handbook site

Repository **Settings → Pages → Source: Deploy from a branch → `main` / `docs`**. The `pages.yml` workflow is included for the Actions-based alternative.

## Contributing

Issues and pull requests are welcome, especially sector profiles, framework crosswalks, and real collector implementations. Keep contributions vendor-neutral: reference a product as an example, never as a requirement.

## Further reading

- [GRC Engineering manifesto](https://grc.engineering/) — the community reference this handbook builds on
- [NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework)
- [FedRAMP Marketplace](https://marketplace.fedramp.gov/) — verify any authorization status you see on a vendor's page
- [StateRAMP](https://stateramp.org/)

---
Maintained by [Docsaf](https://github.com/Docsaf) · [hackingtheworkforce.org](https://www.hackingtheworkforce.org)
