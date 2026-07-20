# Open Source License Compliance Reference

**Status:** Educational guidance tool · Gap-identification use only
**Regulatory content verified:** July 2026 · **Recommended review cadence:** quarterly, or immediately upon a Digital Omnibus / amendment announcement
**Audience:** Engineering, Legal, and Compliance functions at any organization tracking open source usage

> **Legal notice.** This repository scans direct dependencies, classifies
> license risk against your stated business context, and cross-references
> four EU digital regulations for awareness. It does not certify
> compliance, does not issue legal opinions, and does not substitute for
> review by qualified legal counsel. Every risk level and regulatory
> reference should be treated as a starting point for review, not a
> conclusion. Full terms: [DISCLAIMER.md](DISCLAIMER.md).

## The problem

Software projects depend on hundreds of open source libraries. Each one
carries a license with real legal obligations, and most teams cannot answer
"what open source is in this product, and what does it require of us?" on
demand. Regulators are increasingly asking that question too (see
[docs/REGULATORY_CONTEXT.md](docs/REGULATORY_CONTEXT.md)).

## What this tool does

1. **Scans** direct dependencies from `requirements.txt`, `package.json`,
   or a CycloneDX SBOM (`scanner.py`).
2. **Classifies** each license's risk *for your specific context* via a
   short questionnaire -- use case, data handled, target markets, whether
   it's safety-critical, whether it uses AI (`questionnaire.py`).
3. **Assesses** risk per dependency as 🟢 Safe / 🟡 Needs Review /
   🔴 Action Required -- never "compliant" / "non-compliant"
   (`assessor.py`).
4. **Cross-references** applicable EU regulations (CRA, NIS2, EU Data Act,
   AI Act) so findings aren't assessed in isolation (`regulatory_overlay.py`).
5. **Reports** all of the above as a professional PDF, disclaimer included
   on every copy (`reporter.py`).

15 minutes with this tool gets you a complete first-pass inventory and risk
triage -- not a legal sign-off.

## Scope & intended audience

- **Intended for:** engineering teams doing first-pass open source
  inventory, and legal/compliance teams scoping what needs a closer look.
- **Not intended for:** external distribution as a compliance attestation,
  submission to a regulator, or a stand-alone basis for a license
  representation to a customer or auditor.
- **Escalation:** every 🔴 Action Required item, and any 🟡 Needs Review
  item your team can't resolve internally, should go to legal counsel
  before being marked done.

## Design decisions worth knowing about

- **Direct dependencies only.** Transitive dependency trees (50 direct →
  200+ installed) require a real package-manager resolution step this tool
  doesn't perform. Stated in every report, not just here.
- **Context changes risk.** GPL in an internal tool and GPL in a
  distributed product are different legal situations -- the questionnaire
  exists so the tool doesn't produce one generic score per license.
- **No false compliance signals.** The tool identifies gaps; it never says
  "you're compliant." Risk levels are a triage aid.
- **SBOM support.** For code you can't scan directly (vendor/proprietary
  components), supply a CycloneDX SBOM and it's assessed the same way.
- **Accurate terminology.** E.g. "source disclosure requirement," not
  "GPL contamination" -- the latter is legally imprecise and alarmist.
- **Version-aware.** A dependency's license is looked up per package
  *and* version where the data source supports it (SBOM does; the offline
  curated dataset for requirements.txt/package.json currently does not --
  see [DISCLAIMER.md](DISCLAIMER.md)).
- **GPL vs. AGPL, precisely.** GPL's source-disclosure obligation triggers
  on *distribution*; AGPL's also triggers on *network use* (the so-called
  "SaaS loophole" that AGPL was written to close). The assessor and
  regulatory overlay treat these as genuinely different, not
  interchangeable "copyleft."

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```python
from oss_compliance.scanner import DependencyScanner
from oss_compliance.questionnaire import ProductQuestionnaire
from oss_compliance.assessor import ComplianceAssessor
from oss_compliance.reporter import PDFReporter

deps = DependencyScanner().scan_requirements_file("requirements.txt")
context = ProductQuestionnaire().ask_user()  # or build ProductContext directly
report = ComplianceAssessor().assess_dependencies(deps, context)
PDFReporter().generate_report(report, "compliance_report.pdf")
```

Programmatic (no interactive input) and SBOM examples:
[docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md). Sample inputs in `examples/`.

## Testing

```bash
pytest --cov=oss_compliance --cov-report=term-missing
```

72 tests, 96% coverage as of this writing.

## What this tool is NOT

- Not an automated compliance certification system.
- Not a "Compliant / Non-Compliant" verdict provider.
- Not legal advice, and not a substitute for qualified legal counsel.
- Not a full transitive-dependency SCA scanner.

Full disclaimer: [DISCLAIMER.md](DISCLAIMER.md). License primer for the
licenses this tool recognizes: [docs/LICENSE_PRIMER.md](docs/LICENSE_PRIMER.md).

## Regulatory currency note

Regulatory content was verified against EUR-Lex and legislative tracking
sources as of **July 2026**, including the 2026 Digital Omnibus political
agreement deferring AI Act high-risk deadlines. See
[docs/REGULATORY_CONTEXT.md](docs/REGULATORY_CONTEXT.md) for citations and
the specific corrections applied versus commonly circulated (incorrect)
figures for the CRA and EU Data Act regulation numbers/dates.

## Governance & maintenance

- **Content ownership:** treat a legal/compliance function as the required
  reviewer for `oss_compliance/regulatory_overlay.py` and
  `oss_compliance/license_db.py` -- these are the substantive legal content,
  not just code.
- **Review trigger events:** a Digital Omnibus or amending act, a new
  Member State NIS2 transposition, a CRA delegated/implementing act, or
  updated SPDX license data.
- **Reporting an inaccuracy:** open an issue tagged `regulatory-accuracy` or
  `license-data` with a citation to the primary source (SPDX or EUR-Lex ELI
  link preferred).
- **Versioning:** tag a release whenever `license_db.py` or
  `regulatory_overlay.py` content changes, independent of code-only
  releases, so a report can be traced back to the data version that
  produced it.
