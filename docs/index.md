---
title: Building a Trust Center with GRC Engineering
layout: default
description: A handbook page on how to design, build, and run a public Trust Center as an engineered system — controls as code, evidence as data, and trust as a product.
---

## Vision and Mission

Our vision is that trust should be **verifiable, not asserted**. A customer, auditor, or regulator should be able to see how we are secured today — not how we were secured the last time someone updated a PDF.

Our mission is to run the Trust Center as a **product built on an engineered GRC pipeline**: every claim on the public page traces to a control, every control traces to machine-collected evidence, and every change goes through version control and review.

This applies whether the reader is a Fortune 500 procurement team evaluating a SaaS vendor, a state CIO's office reviewing a GovTech supplier, a school board asking how student data is protected, or a federal authorizing official reading a System Security Plan. The audiences differ; the engineering does not. It is achieved through six GRC Engineering operating principles:

1. **Controls as code** with a focus on:
   - One control catalog (YAML) as the single source of truth — the Trust Center, questionnaires, and audit packages are *views* of it
   - Every control maps to the frameworks that matter to *your* buyers at the time it is written, not at audit time — SOC 2, ISO 27001, NIST CSF 2.0, and CIS v8.1 for commercial customers; NIST SP 800-53, FedRAMP, StateRAMP/TX-RAMP, CJIS, and FERPA for public-sector ones
   - Pull requests, not meetings, to change a control's status, owner, or evidence
1. **Evidence as data** with a focus on:
   - Collect evidence from APIs (cloud, IdP, EDR, ticketing, CI) on a schedule — humans review, robots gather
   - Store evidence with a timestamp, a source, a hash, and the control ID it satisfies
   - Prefer continuous signals (MFA enforcement rate, patch SLA compliance) over point-in-time screenshots
1. **Transparency by default** with a focus on:
   - Publish what customers ask about most: subprocessors, uptime, pen-test cadence, incident history, data-residency
   - Draw a hard line around MNPI and internal-only artifacts; gate them behind NDA-click-through, never hide them behind "ask sales"
   - In the public sector, treat transparency as a legal posture, not just a sales one: assume public-records requests, publish what a FOIA response would reveal anyway, and keep the sensitive tier (SSPs, POA&Ms, network diagrams) properly marked and off the public site
   - Show the *date* and *source* next to every metric so readers can judge staleness themselves
1. **Risk reduction over decoration** with a focus on:
   - A red control on an internal dashboard beats a green badge on a public page
   - Fix root causes in the pipeline (a failed collector, an unowned control) rather than patch the rendered site
   - Secure by default: the Trust Center is static, read-only, and has no inbound attack surface beyond a form handler
1. **Boring, reusable solutions** with a focus on:
   - Static site + CI + object storage. No bespoke platform until the spreadsheet stops scaling
   - Reuse the same catalog for questionnaires (SIG, CAIQ), customer DDQs, and audit evidence requests
   - Buy a Trust Center vendor only when it saves more engineering time than it costs in lock-in
1. **Scaling through AI, safely** with a focus on:
   - Use LLMs to draft questionnaire answers *from the catalog* with citations back to control IDs — never free-form
   - Automate first-pass control-to-framework mapping and evidence classification; a human approves the PR
   - Treat AI outputs as untrusted input: validated schema, reviewed diff, logged prompt

### Program Structure

A Trust Center that is engineered rather than written is organized around four functions. Each has an owner, a repository path, and a definition of done.

<table id="Sub-Departments">
  <tr>
    <th class="text-center">
        <h5><a href="build-guide.html#phase-1-control-catalog">Control Catalog</a></h5>
    </th>
    <th class="text-center">
        <h5><a href="build-guide.html#phase-2-evidence-pipeline">Evidence Pipeline</a></h5>
    </th>
    <th class="text-center">
        <h5><a href="build-guide.html#phase-3-trust-center-site">Trust Center Site</a></h5>
    </th>
    <th class="text-center">
        <h5><a href="build-guide.html#phase-4-customer-assurance">Customer Assurance</a></h5>
    </th>
  </tr>
  <tr>
      <td>
        <ul>
            <li>Control definitions (YAML)</li>
            <li>Framework crosswalks (SOC 2, ISO 27001, NIST CSF, CIS, NIST 800-53, FedRAMP, StateRAMP, CJIS)</li>
            <li>Policy-as-code checks (schema, ownership, freshness)</li>
            <li>Risk register linkage</li>
        </ul>
      </td>
      <td>
        <ul>
            <li>Scheduled collectors (cloud, IdP, EDR, CI, ticketing)</li>
            <li>Evidence store (hashed, timestamped, immutable)</li>
            <li>Control health scoring</li>
            <li>Drift and staleness alerts</li>
        </ul>
      </td>
      <td>
        <ul>
            <li>Static site generated from the catalog</li>
            <li>Public tier vs. NDA tier</li>
            <li>Subprocessor, uptime, and incident pages</li>
            <li>Document vault (SOC 2 report, pen-test letter, policies)</li>
        </ul>
      </td>
      <td>
        <ul>
            <li>Questionnaire answer bank (SIG, CAIQ, HECVAT, custom DDQs, RFP security sections)</li>
            <li>AI-assisted drafting with control citations</li>
            <li>Access-request and NDA workflow</li>
            <li>Sales enablement and response SLAs</li>
        </ul>
      </td>
  </tr>
</table>

#### Define the Truth — The Control Catalog

The [Control Catalog](build-guide.html#phase-1-control-catalog) is the primary artifact. It is a directory of YAML files, one per control, each declaring an ID, an owner, an implementation statement, the frameworks it satisfies, the evidence it requires, and the frequency at which that evidence must be refreshed. Nothing appears on the Trust Center that does not trace to a control here. Changing the catalog is a pull request with a required reviewer from the security function; the CI job rejects controls with no owner, no evidence definition, or a broken framework reference.

#### Prove the Truth — The Evidence Pipeline

The [Evidence Pipeline](build-guide.html#phase-2-evidence-pipeline) turns claims into data. Scheduled jobs call the APIs of the systems that actually enforce the control — the identity provider for MFA coverage, the cloud account for encryption and logging configuration, the endpoint platform for agent coverage, the vulnerability scanner for SLA adherence — and write normalized JSON records to an evidence store. Each record carries a SHA-256 hash and a collection timestamp. A control is *healthy* when its latest evidence is within its freshness window and passes its assertion; it is *degraded* or *failed* otherwise, and the pipeline opens a ticket rather than quietly publishing a stale green.

#### Show the Truth — The Trust Center Site

The [Trust Center Site](build-guide.html#phase-3-trust-center-site) is a static site rendered from the catalog and the evidence store on every merge and on a daily schedule. The public tier shows posture summaries, certifications, subprocessors, uptime, and the incident and vulnerability disclosure processes. The NDA tier, gated by a click-through agreement and an email-verified link, exposes the SOC 2 report, penetration-test attestation, full policy set, and per-control detail. Because the site is static there is no application to patch, no database to breach, and no admin panel to phish.

#### Answer the Customer — Customer Assurance

[Customer Assurance](build-guide.html#phase-4-customer-assurance) closes the loop with the buyer. Security questionnaires are answered from an answer bank generated from the catalog, with each answer citing the control ID it derives from; when the control changes, the answer is flagged for regeneration. AI drafting is permitted only against that bank. Access requests, NDA acceptance, and document downloads are logged so the team can report which prospects looked at what, and which questions the Trust Center still fails to answer without a human — that list is the roadmap.

In the public sector the "customer" is often a procurement office, a state or district security review, or an authorizing official, and the questionnaire is an RFP security section, a HECVAT, a student-data-privacy agreement, or a control-by-control SSP request. The same answer bank serves them; only the crosswalk and the output template change.

### Who this is for

| Reader | What the Trust Center must do for them |
|---|---|
| **Enterprise SaaS vendor** | Shorten security review cycles; replace questionnaire ping-pong with a link; keep SOC 2 / ISO evidence current between audits |
| **GovTech vendor** (selling to federal, state, local, education) | Show FedRAMP / StateRAMP / TX-RAMP status honestly, including "in process"; publish CJIS, FERPA, and data-residency positions; be ready for public-records exposure of what you submit |
| **Public agency or school district** | Demonstrate stewardship of resident and student data to boards, councils, and parents; satisfy state audit and cyber-insurance requirements; give vendors a clear bar to meet |
| **Federal program or contractor** | Feed the SSP, POA&M, and continuous-monitoring deliverables from the same catalog and evidence store the public page uses, so the ATO package and the public narrative never diverge |

### Contacting the Team

#### Reporting a security concern

Vulnerability reports go through the disclosure process published on the Trust Center's **Security Disclosure** page. Reports are acknowledged within two business days and tracked to closure in the same catalog that drives the public page, so remediation status is never a separate spreadsheet.

#### Requesting documents or NDA-tier access

Use the access-request form on the Trust Center. Requests are reviewed by the security function, not sales, and the standard turnaround is one business day. Approved access expires; it is not permanent.

#### Reporting an incident

If you believe customer data or a production system has been affected, follow the incident response runbook and page the on-call responder. Public status is published to the Trust Center's incident page only after severity has been assessed and communications have been approved by the incident commander.

---

#### Where to go next

- **Start building:** the [step-by-step build guide](build-guide.html) covers each phase with repository layout, schemas, CI workflows, and definitions of done.
- **See the code:** the `trust-center/` directory in this repository contains a working starter catalog, an example evidence collector, and the GitHub Actions workflows that validate and publish it.
- **Adopt the mindset:** the [GRC Engineering manifesto](https://grc.engineering/) is the community reference this handbook builds on.
