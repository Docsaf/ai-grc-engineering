---
title: Build Guide — Trust Center as Code
layout: default
description: Phase-by-phase instructions for standing up a Trust Center on a GRC Engineering pipeline, with repository layout, schemas, CI workflows, and definitions of done.
---

[← Back to the handbook page](index.html)

This guide is sector-neutral. It is written to be executed by one security engineer with part-time help from IT and platform engineering, in roughly 8–12 weeks to a public v1, whether the organization is a cloud-native SaaS company, a GovTech vendor pursuing a FedRAMP or StateRAMP authorization, a public agency, or a school district. Pick the profile below that matches you; it decides which frameworks you crosswalk to and what your public and restricted tiers must contain. Everything else is the same.

The four phases build on each other. Do not skip to Phase 3 — a beautiful static site with hand-typed claims is the thing this approach exists to replace.

## Sector profiles

| Profile | Primary frameworks to crosswalk | Public tier must include | Restricted tier must include | Typical evidence sources |
|---|---|---|---|---|
| **Enterprise SaaS** | SOC 2, ISO 27001:2022, NIST CSF 2.0, CIS v8.1; add PCI DSS / HIPAA if in scope | Subprocessors, certifications with dates, uptime, disclosure process, incident history | SOC 2 report, pen-test letter, policies, per-control detail, completed SIG/CAIQ | IdP, cloud provider, EDR, scanner, CI, ticketing, HRIS |
| **GovTech vendor** | NIST SP 800-53 Rev. 5 (Moderate baseline), FedRAMP / StateRAMP / TX-RAMP, CJIS if law-enforcement data, FERPA / state student-privacy laws if education | Authorization status (including "in process" and the 3PAO engaged), data residency (U.S.-only, GovCloud), CJIS/FERPA positions, subprocessors, disclosure process | SSP excerpts, POA&M summary, SAR letter, continuous-monitoring cadence, customer-responsibility matrix | Same as SaaS plus the GovCloud/sovereign account, vulnerability scans in the ConMon format, ticketing for POA&M items |
| **Public agency / municipality** | NIST CSF 2.0, CIS v8.1 (IG1/IG2), state cyber standards, cyber-insurance questionnaire, CJIS if applicable | Resident-data handling, vendor security requirements, incident notification commitments, public status page | Internal control detail, vendor assessments, audit findings and remediation status | IdP, endpoint, backup platform, vulnerability scanner, vendor-risk register |
| **K-12 / higher education** | NIST CSF 2.0, CIS v8.1, FERPA, COPPA, state student-data-privacy laws, HECVAT (higher ed) | Student-data-privacy commitments, approved-vendor list, parent-facing FAQ, incident notification commitments | Vendor DPAs, HECVAT responses, internal control detail, audit findings | Student information system, IdP, endpoint (including 1:1 devices), vendor-risk register, LMS |
| **Federal program / contractor** | NIST SP 800-53 Rev. 5, NIST SP 800-171 / CMMC if CUI, agency overlays | Authorization boundary summary, program security contact, disclosure process | SSP, POA&M, ConMon reports, control implementation statements | Agency-approved scanners, SIEM, IdP (PIV/CAC), ticketing |

Two rules that hold across every profile. First, **never publish a status you cannot evidence** — "FedRAMP Ready" and "FedRAMP In Process" are distinct, dated, and verifiable on the Marketplace; do not blur them. Second, **assume public-records exposure** in any public-sector deal: what you submit in an RFP response may be released under FOIA or a state equivalent, so write the restricted tier as if a competitor will eventually read it and mark it accordingly.

## Repository layout

```text
ai-grc-engineering/
├── docs/                         # GitHub Pages site (this handbook)
├── trust-center/
│   ├── controls/                 # one YAML file per control (the catalog)
│   ├── frameworks/               # crosswalk tables: framework → control IDs
│   ├── evidence/                 # collected evidence (JSON), committed or synced from object storage
│   ├── policies/                 # published policy set (markdown), versioned
│   ├── answers/                  # questionnaire answer bank generated from controls
│   └── site/                     # static site templates for the public Trust Center
├── scripts/
│   ├── validate_controls.py      # schema + ownership + freshness checks (runs in CI)
│   ├── collect_evidence.py       # calls system APIs, writes normalized evidence records
│   ├── score_controls.py         # computes control health from evidence
│   └── render_site.py            # renders trust-center/site from catalog + evidence
└── .github/workflows/
    ├── validate.yml              # PR gate: catalog must be valid
    ├── evidence.yml              # scheduled collection + scoring
    └── pages.yml                 # deploy docs/ to GitHub Pages
```

---

## Phase 1: Control Catalog

**Goal:** one machine-readable source of truth for every control you will ever claim.

### 1.1 Define the control schema

Each control is a YAML file. Keep the schema small enough that engineers will actually fill it in.

```yaml
# trust-center/controls/IAM-02.yaml
id: IAM-02
title: Multi-factor authentication is enforced for all workforce identities
domain: Identity & Access
owner: it-operations            # a team, not a person
status: implemented             # planned | partial | implemented | not-applicable
public: true                    # appears on the public tier
statement: >
  All workforce accounts in the corporate identity provider are required to
  authenticate with phishing-resistant MFA. Exceptions are time-boxed and
  approved by the security function.
frameworks:
  soc2: [CC6.1, CC6.6]
  iso27001_2022: [A.5.17, A.8.5]
  nist_csf_2: [PR.AA-03]
  cis_v8_1: ["6.3", "6.5"]
  nist_800_53_r5: [IA-2(1), IA-2(2)]   # public-sector crosswalk; FedRAMP/StateRAMP inherit from here
evidence:
  - id: idp-mfa-coverage
    source: okta            # collector name in scripts/collect_evidence.py
    assertion: "mfa_enforced_pct >= 99"
    freshness_days: 7
risks: [R-014]
```

### 1.2 Write the validator

`scripts/validate_controls.py` runs on every pull request and fails the build if any control is missing an owner, has an unknown framework reference, references an evidence collector that does not exist, or has a `public: true` flag with `status: planned` (you do not publish plans as posture).

### 1.3 Build the framework crosswalks

Generate `trust-center/frameworks/*.md` from the catalog — never maintain them by hand. A SOC 2 crosswalk is simply "for each criterion, list the controls whose `frameworks.soc2` includes it." Gaps show up as criteria with zero controls, which is your remediation backlog.

### 1.4 Seed the catalog

Start with the 30–40 controls your buyers actually ask about (enterprise procurement, state security reviews, school-district privacy offices, or authorizing officials — see the sector profiles above), grouped by domain: identity and access, endpoint, cloud configuration, logging and monitoring, vulnerability management, change management, incident response, business continuity, vendor risk, data protection, secure development, and security awareness. Import from your existing policies and your last audit's control list — or, in the public sector, from your SSP's control implementation statements; do not invent controls you have not implemented.

**Definition of done:** the validator passes, every control has an owner who has acknowledged ownership in the PR, and at least one crosswalk renders with no orphaned criteria in the frameworks you claim.

---

## Phase 2: Evidence Pipeline

**Goal:** every `public: true` control is backed by evidence a machine collected in the last freshness window.

### 2.1 Choose collectors

Start with the systems that enforce the most controls per API call:

| System | Evidence produced | Controls typically satisfied |
|---|---|---|
| Identity provider (Okta / Entra ID) | MFA enforcement rate, dormant accounts, admin count, SSO app coverage | IAM-01…IAM-06 |
| Cloud provider (AWS Config / Azure Policy / GCP SCC) | encryption at rest, public buckets, logging enabled, root-key usage | CLD-01…CLD-08 |
| Endpoint platform (CrowdStrike / SentinelOne / Intune) | agent coverage, disk encryption, OS patch age | END-01…END-04 |
| Vulnerability scanner | open criticals by age, SLA compliance | VUL-01…VUL-03 |
| Source control / CI | branch protection, required reviews, secret scanning, SAST | SDL-01…SDL-05 |
| Ticketing (Jira / ServiceNow) | change approvals, incident closure times, access reviews | CHG-01, IR-02, IAM-07 |
| HRIS | onboarding/offboarding timeliness, training completion | HR-01, AWR-01 |

### 2.2 Normalize the evidence record

Every collector writes the same shape:

```json
{
  "evidence_id": "idp-mfa-coverage",
  "control_ids": ["IAM-02"],
  "collected_at": "2026-09-15T06:00:00Z",
  "source": "okta",
  "metrics": { "mfa_enforced_pct": 99.6, "total_users": 412, "exceptions": 2 },
  "raw_ref": "s3://grc-evidence/okta/2026-09-15/mfa.json",
  "sha256": "…"
}
```

Raw API responses go to write-once object storage with retention matching your audit window (typically 13 months for SOC 2 Type II; for FedRAMP continuous monitoring, retain per the agency's records schedule, commonly three years). Only the normalized record is committed to the repository.

### 2.3 Score control health

`scripts/score_controls.py` evaluates each control's `assertion` against its latest evidence:

- **Healthy** — evidence within `freshness_days` and assertion passes
- **Degraded** — evidence fresh but assertion fails, or evidence stale by less than 2× the window
- **Failed** — no evidence, or stale by more than 2× the window

Failed and degraded controls open a ticket to the owner automatically. Public rendering of a failed control is blocked; the site shows the last healthy date rather than a false green.

### 2.4 Secure the pipeline

Collectors run in GitHub Actions with OIDC-federated, read-only cloud roles — no long-lived API keys in secrets. The evidence bucket denies delete. The workflow that writes evidence cannot also change the catalog.

**Definition of done:** at least 80% of `public: true` controls are Healthy on the scheduled run, and the remaining 20% have open tickets with owners.

---

## Phase 3: Trust Center Site

**Goal:** a public, static, read-only site rendered from the catalog and evidence — never hand-edited.

### 3.1 Information architecture

Two tiers. Decide up front what goes where and encode it in the catalog with the `public` flag and a `tier` field on documents.

**Public tier**

- Posture overview: control domains with health rollups (counts, not per-control detail)
- Certifications and attestations: SOC 2 Type II, ISO 27001, Cyber Essentials Plus — with issue and expiry dates
- Subprocessors: name, purpose, region, date added; with a change-notification signup
- Data residency and encryption summary
- Uptime (linked or embedded from the status page)
- Security disclosure process and PGP key
- Incident history: dated, customer-impacting incidents with post-incident summaries
- Penetration-test cadence and the date of the most recent test
- For GovTech: authorization status by program (FedRAMP, StateRAMP, TX-RAMP) with the Marketplace or program listing linked, impact level, and 3PAO
- For agencies and districts: resident- or student-data-privacy commitments, incident notification timelines, and vendor security requirements

**NDA tier** (click-through agreement + verified email link, expiring)

- SOC 2 report, ISO certificate and Statement of Applicability, pen-test attestation letter
- Full policy set (versioned, with change log)
- Per-control detail with evidence summaries and last-collected timestamps
- Completed SIG / CAIQ / HECVAT
- For GovTech: SSP excerpts, POA&M summary, customer-responsibility matrix, most recent SAR letter

### 3.2 Render, don't write

`scripts/render_site.py` produces `trust-center/site/` from templates. It runs on every merge to `main` and on the daily evidence schedule. If rendering fails, the previous deploy stays up — a stale site is better than a broken one, and staleness is visible because every metric carries its `collected_at` date.

### 3.3 Hosting

GitHub Pages is sufficient for v1 of the public tier. For the NDA tier, use object storage behind a CDN with signed, expiring URLs issued by a small serverless handler that records the requester's email and the agreement version accepted. Do not run a web application. Do not attach a database.

### 3.4 Buy vs. build

Commercial Trust Center platforms (Vanta, Drata, SafeBase, Conveyor and similar) are a reasonable choice for commercial vendors; public agencies should also check whether their state offers a shared GRC platform before buying once questionnaire volume exceeds roughly 10 per month or the sales team needs self-service. Even then, keep the catalog and evidence pipeline in your own repository and treat the vendor as a rendering and distribution layer. The vendor should ingest *your* catalog; your posture should never live only in someone else's product.

**Definition of done:** the public tier is live at a custom domain with HSTS, every metric shows a source and date, and a security-aware reviewer outside the team can find subprocessors, disclosure process, and certification dates in under two minutes.

---

## Phase 4: Customer Assurance

**Goal:** answer questionnaires from the catalog, with citations, faster than the buyer expects.

### 4.1 Generate the answer bank

For each control, generate one or more canonical answers keyed to common questionnaire items (SIG Lite, CAIQ v4, HECVAT, state RFP security sections, and the ten custom DDQs you see most). Each answer cites its control ID and inherits the control's health. When a control changes, its answers are marked `needs-review` and cannot be sent until a human re-approves them.

### 4.2 AI-assisted drafting with guardrails

Allow an LLM to draft answers to *new* questions only by retrieving from the answer bank and catalog, and require it to cite control IDs in every sentence that makes a claim. Reject drafts with uncited claims in CI. Log every prompt and output. Never let a model see, or answer from, the raw evidence bucket.

### 4.3 Access and NDA workflow

Access requests arrive from the Trust Center form, land in the ticketing system, and are approved by the security function with a one-business-day SLA. Approval issues a signed link valid for 14 days. Every download is logged with requester, document, version, and time — this log is itself evidence for your vendor-management and data-classification controls.

### 4.4 Measure and feed the roadmap

Track weekly: questionnaires received, median time to return, percentage of questions answered directly from the bank, and the top ten questions that required a human. That last list tells you which controls to add or clarify next quarter.

**Definition of done:** 80% of questionnaire items answered from the bank without edits, median turnaround under five business days, and zero answers sent that cite a Failed control.

---

## Operating cadence

| Cadence | Activity | Output |
|---|---|---|
| Continuous | PR validation of catalog changes | Green check or blocked merge |
| Daily | Evidence collection, scoring, site render | Updated Trust Center; tickets for Degraded/Failed |
| Weekly | Review Failed controls and open questionnaire gaps | Owner follow-ups; answer-bank additions |
| Monthly | Subprocessor and policy change review; access-log review | Change notifications sent; log retained as evidence |
| Quarterly | Framework crosswalk gap review; pen-test scheduling; Trust Center content audit | Remediation backlog; updated attestations |
| Annually | Audit evidence package generated from the evidence store | Auditor request list satisfied from repository |

## Common failure modes

- **Hand-editing the rendered site.** The fix never makes it back to the catalog and the next render erases it. Lock the site directory in CI.
- **Evidence without assertions.** A screenshot in a folder is not evidence of anything. Every evidence definition needs a testable assertion.
- **Controls without owners.** Ownerless controls decay silently. The validator should refuse them.
- **Publishing plans as posture.** "Planned" controls belong in a roadmap, not on a page a buyer reads as current state.
- **Letting the vendor own the truth.** If your catalog lives only inside a commercial platform, you have outsourced your security narrative.

---

## Starter code in this repository

- `trust-center/controls/` — three example controls in the schema above
- `scripts/validate_controls.py` — the PR gate
- `scripts/collect_evidence.py` — a collector skeleton with a stub `okta` source
- `.github/workflows/validate.yml`, `evidence.yml`, `pages.yml` — the CI backbone

Clone, replace the stub collectors with real API calls, and open your first PR.
