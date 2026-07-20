# Usage Guide

## 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Scan dependencies

```python
from oss_compliance.scanner import DependencyScanner

scanner = DependencyScanner()
deps = scanner.scan_requirements_file("requirements.txt")
# or:
deps = scanner.scan_package_json("package.json")
# or, for vendor/proprietary code you can't scan directly:
deps = scanner.scan_sbom_file("sbom.json")
```

Each call returns a `List[Dependency]`. Unresolved licenses come back as
`Dependency.license = None`, `license_id = "Unknown"` -- an explicit signal,
not a silent guess.

## 3. Capture business context

Interactively:

```python
from oss_compliance.questionnaire import ProductQuestionnaire

context = ProductQuestionnaire().ask_user()
```

Or build a `ProductContext` directly for scripting:

```python
from oss_compliance.models import ProductContext

context = ProductContext(
    product_name="Predictive Maintenance Service",
    use_case="SaaS",                       # Internal / Embedded / SaaS / Distributed
    data_types=["Industrial/operational data"],
    target_markets=["EU"],
    is_safety_critical=False,
    has_ai=True,
    modifications_expected=False,
)
```

`use_case` drives most of the risk logic -- see
[LICENSE_PRIMER.md](LICENSE_PRIMER.md) for what each value changes.

## 4. Assess risk

```python
from oss_compliance.assessor import ComplianceAssessor

report = ComplianceAssessor().assess_dependencies(deps, context)

for dep in report.dependencies:
    print(dep.risk_level_for_context(context), dep.name, dep.version, dep.license_id)

print(report.risk_summary)          # {"🟢 Safe": 41, "🟡 Needs Review": 3, "🔴 Action Required": 2}
print(report.actions_required)      # human-readable reasons for each 🔴 item
print(report.regulatory_references) # applicable EU regulations, with citations
```

## 5. Generate the PDF report

```python
from oss_compliance.reporter import PDFReporter

PDFReporter().generate_report(report, "compliance_report.pdf")
```

The disclaimer is rendered on every report and cannot be suppressed.

## Sample data

`examples/sample_requirements.txt`, `examples/sample_package.json`, and
`examples/sample_sbom.json` are ready-made inputs covering permissive,
weak-copyleft, strong-copyleft, network-copyleft, and unknown licenses, so
you can see every risk tier in one run.
