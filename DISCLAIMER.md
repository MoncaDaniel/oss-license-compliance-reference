# Disclaimer

This repository is a **guidance tool**, not a certification tool. Read this
before acting on any output it produces.

## What this tool IS

- An automated scanner for licenses declared in **direct** dependencies
  (requirements.txt, package.json, or a CycloneDX SBOM).
- A context-aware risk triage: the same license can be low-risk in one
  business context and high-risk in another, so the tool asks about your
  use case before assigning a risk level.
- A generator of a professional PDF report identifying what needs legal
  review, with a disclaimer on every report.
- A reference for how open source findings intersect with four EU digital
  regulations (CRA, NIS2, EU Data Act, AI Act), for awareness -- not scope
  determination.

## What this tool is NOT

- **Not** an automated compliance certification system.
- **Not** legal advice or a legal opinion.
- **Not** a guarantee of regulatory approval.
- **Not** a replacement for qualified legal counsel.
- **Not** a full software composition analysis (SCA) tool -- it does not
  resolve the transitive dependency tree (see limitation below).

## Known limitations (stated up front, not buried)

- **Direct dependencies only.** A requirements.txt or package.json with 50
  direct entries commonly implies 200+ installed packages once transitive
  dependencies resolve. This tool does not walk that tree. If your project
  needs transitive-dependency visibility, pair this tool with a full SCA
  scanner (e.g. one that reads a lockfile or dependency graph) or supply a
  complete SBOM instead.
- **Offline license lookup is a curated dataset, not a live registry.** For
  requirements.txt/package.json input, license resolution uses a small
  built-in dataset of commonly seen packages. Anything not in that dataset
  resolves to "Unknown" -- an explicit signal to investigate, not a silent
  guess. SBOM input carries vendor-declared license data directly and does
  not depend on this dataset.
- **Risk levels are triage, not verdicts.** 🟢 Safe / 🟡 Needs Review /
  🔴 Action Required describe how urgently a human should look at
  something, not whether you are "compliant."

## Required disclaimer text

Every generated report includes:

> This tool provides regulatory guidance only. Final compliance assessment
> requires review by qualified legal counsel. Regulatory requirements vary
> by jurisdiction and product context.

## Currency of regulatory content

Regulatory content in `oss_compliance/regulatory_overlay.py` was checked
against EUR-Lex and legislative tracking sources as of July 2026, including
the 2026 Digital Omnibus deferral of AI Act high-risk deadlines. EU digital
regulation is under active amendment. Re-verify dates, citations, and
penalty figures before relying on them for a real filing, audit response,
or contractual representation.
