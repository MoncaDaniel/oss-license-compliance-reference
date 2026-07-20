"""Risk assessment logic (Anomaly #3): this module identifies gaps and
assigns a triage risk level. It never claims "you are compliant" -- only
"here is what applies, and here is what needs legal review."

Risk level reference:
  SAFE   -- no obligation triggered by this license in this context
  REVIEW -- an obligation may be triggered; verify before treating as clear
  ACTION -- an obligation is triggered; route to legal counsel
"""

from typing import List

from .models import RISK_ACTION, RISK_REVIEW, RISK_SAFE, ComplianceReport, Dependency, ProductContext
from .regulatory_overlay import RegulatoryOverlay


def risk_level_for_dependency(dep: Dependency, context: ProductContext) -> str:
    """Core per-dependency risk logic. Kept as a free function (rather than
    only a method) so both Dependency.risk_level_for_context and
    ComplianceAssessor can share one implementation."""
    license_ = dep.license

    if license_ is None:
        return RISK_ACTION  # Unknown license: must be identified before use.

    base = license_.risk_level_base

    if base == "Permissive":
        return RISK_SAFE

    if base == "Weak Copyleft":
        if not license_.applies_to_context(context):
            return RISK_SAFE
        return RISK_ACTION if context.modifications_expected else RISK_REVIEW

    if base == "Strong Copyleft":
        if context.use_case == "Internal":
            return RISK_SAFE
        if context.use_case == "SaaS":
            return RISK_REVIEW
        return RISK_ACTION  # Embedded / Distributed: distribution has occurred.

    if base == "Network Copyleft":
        if context.use_case in ("SaaS", "Distributed", "Embedded"):
            return RISK_ACTION
        return RISK_REVIEW  # Internal: network exposure can't be ruled out from context alone.

    return RISK_ACTION  # Unrecognized category: fail safe, don't guess.


class ComplianceAssessor:
    """Aggregates per-dependency risk into a full ComplianceReport."""

    def __init__(self):
        self._overlay = RegulatoryOverlay()

    def assess_dependencies(
        self, dependencies: List[Dependency], context: ProductContext
    ) -> ComplianceReport:
        report = ComplianceReport(
            product_name=context.product_name,
            context=context,
            dependencies=list(dependencies),
        )

        for dep in dependencies:
            risk = dep.risk_level_for_context(context)
            report.risk_summary[risk] = report.risk_summary.get(risk, 0) + 1

            if risk == RISK_ACTION:
                reason = self._overlay.get_license_implications(dep.license, context)
                license_label = dep.license.name if dep.license else "Unknown license"
                report.actions_required.append(f"{dep.name} {dep.version} ({license_label}): {reason}")

        report.regulatory_references = self._overlay.get_applicable_regulations(context)

        return report
