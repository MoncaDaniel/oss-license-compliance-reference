"""Data structures for the OSS License Compliance Reference tool.

Plain data containers. Risk *logic* lives in assessor.py; these classes hold
just enough behavior (applies_to_context / risk_level_for_context) to keep
the license-specific nuance next to the license data itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

# Canonical risk-level labels used across assessor.py and reporter.py.
RISK_SAFE = "🟢 Safe"
RISK_REVIEW = "🟡 Needs Review"
RISK_ACTION = "🔴 Action Required"


@dataclass
class ProductContext:
    """Business context that determines whether a license's restrictions
    actually bite. The same license can be 🟢 in one context and 🔴 in
    another -- this is the input that makes the assessment context-aware
    instead of a generic per-license score."""

    product_name: str = ""
    use_case: str = "Internal"  # "Internal" / "Embedded" / "SaaS" / "Distributed"
    data_types: List[str] = field(default_factory=list)
    target_markets: List[str] = field(default_factory=list)
    is_safety_critical: bool = False
    has_ai: bool = False
    modifications_expected: bool = False


@dataclass
class License:
    """A single license as tracked in the local SPDX-derived database.

    `full_text` is intentionally omitted in favor of `reference_url`: copyleft
    license texts (e.g. GPL-3.0, AGPL-3.0) run to tens of kilobytes, and
    vendoring them verbatim adds bulk without adding accuracy -- the
    authoritative text is the one at the SPDX/OSI URL, not a copy we might
    let drift out of sync. `summary` is a short, plain-English paraphrase for
    display only.
    """

    name: str
    spdx_id: str
    summary: str
    reference_url: str
    risk_level_base: str  # "Permissive" / "Weak Copyleft" / "Strong Copyleft" / "Network Copyleft"
    source_disclosure_requirement: bool
    modifications_allowed: bool
    commercial_use_allowed: bool
    key_restrictions: List[str] = field(default_factory=list)
    # Distinguishes AGPL-style "network use" triggers from GPL-style
    # "distribution" triggers -- this is the crux of the GPL-vs-SaaS anomaly.
    triggers_on_network_use: bool = False
    triggers_on_distribution: bool = False

    def applies_to_context(self, context: ProductContext) -> bool:
        """Does this license's copyleft/disclosure obligation actually
        trigger for this context? (Not: "is this license present" -- that's
        always true if it's a dependency. This asks whether its *conditions*
        are met.)"""
        if not self.source_disclosure_requirement:
            return False
        if self.triggers_on_network_use and context.use_case in ("SaaS", "Distributed", "Embedded"):
            return True
        if self.triggers_on_distribution and context.use_case in ("Distributed", "Embedded"):
            return True
        return False


@dataclass
class Dependency:
    """One scanned dependency with its resolved license."""

    name: str
    version: str
    license_id: str
    license: Optional[License]
    source: str = ""  # "PyPI", "npm", "SBOM", etc.

    def risk_level_for_context(self, context: ProductContext) -> str:
        """Delegates to assessor logic via a late import to avoid a
        models<->assessor circular import while keeping the call site
        convenient (`dep.risk_level_for_context(context)`)."""
        from .assessor import risk_level_for_dependency

        return risk_level_for_dependency(self, context)


@dataclass
class ComplianceReport:
    """The full output of a scan + assessment run."""

    product_name: str = ""
    scan_date: datetime = field(default_factory=datetime.utcnow)
    context: Optional[ProductContext] = None
    dependencies: List[Dependency] = field(default_factory=list)
    risk_summary: Dict[str, int] = field(
        default_factory=lambda: {RISK_SAFE: 0, RISK_REVIEW: 0, RISK_ACTION: 0}
    )
    regulatory_references: List[str] = field(default_factory=list)
    actions_required: List[str] = field(default_factory=list)
    disclaimer: str = (
        "This tool provides regulatory guidance only. Final compliance assessment "
        "requires review by qualified legal counsel. Regulatory requirements vary by "
        "jurisdiction and product context."
    )
