"""Tests for risk assessment logic."""

from oss_compliance.assessor import ComplianceAssessor, risk_level_for_dependency
from oss_compliance.license_db import get_license
from oss_compliance.models import RISK_ACTION, RISK_REVIEW, RISK_SAFE, Dependency, ProductContext


def dep_with_license(spdx_id, name="lib", version="1.0"):
    return Dependency(name=name, version=version, license_id=spdx_id, license=get_license(spdx_id))


def unknown_dep(name="mystery-lib", version="1.0"):
    return Dependency(name=name, version=version, license_id="Unknown", license=None)


def test_mit_safe_in_any_context(internal_context, saas_context, distributed_context, embedded_context):
    dep = dep_with_license("MIT")
    for ctx in (internal_context, saas_context, distributed_context, embedded_context):
        assert risk_level_for_dependency(dep, ctx) == RISK_SAFE


def test_apache_2_safe_in_any_context(internal_context, distributed_context):
    dep = dep_with_license("Apache-2.0")
    assert risk_level_for_dependency(dep, internal_context) == RISK_SAFE
    assert risk_level_for_dependency(dep, distributed_context) == RISK_SAFE


def test_gpl_distributed_is_action(distributed_context):
    dep = dep_with_license("GPL-3.0-only")
    assert risk_level_for_dependency(dep, distributed_context) == RISK_ACTION


def test_gpl_internal_is_safe(internal_context):
    dep = dep_with_license("GPL-3.0-only")
    assert risk_level_for_dependency(dep, internal_context) == RISK_SAFE


def test_gpl_saas_is_review(saas_context):
    dep = dep_with_license("GPL-3.0-only")
    assert risk_level_for_dependency(dep, saas_context) == RISK_REVIEW


def test_gpl_embedded_is_action(embedded_context):
    dep = dep_with_license("GPL-2.0-only")
    assert risk_level_for_dependency(dep, embedded_context) == RISK_ACTION


def test_agpl_saas_is_action(saas_context):
    dep = dep_with_license("AGPL-3.0-only")
    assert risk_level_for_dependency(dep, saas_context) == RISK_ACTION


def test_agpl_distributed_is_action(distributed_context):
    dep = dep_with_license("AGPL-3.0-only")
    assert risk_level_for_dependency(dep, distributed_context) == RISK_ACTION


def test_agpl_internal_is_review_not_safe(internal_context):
    """AGPL's network-use trigger doesn't cleanly map to 'internal use is
    always safe' -- internal deployments can still expose users over a
    network. This should never silently resolve to Safe."""
    dep = dep_with_license("AGPL-3.0-only")
    assert risk_level_for_dependency(dep, internal_context) == RISK_REVIEW


def test_unknown_license_is_action(internal_context):
    dep = unknown_dep()
    assert risk_level_for_dependency(dep, internal_context) == RISK_ACTION


def test_lgpl_internal_is_safe(internal_context):
    dep = dep_with_license("LGPL-3.0-only")
    assert risk_level_for_dependency(dep, internal_context) == RISK_SAFE


def test_lgpl_distributed_with_modifications_is_action():
    ctx = ProductContext(use_case="Distributed", modifications_expected=True)
    dep = dep_with_license("LGPL-2.1-only")
    assert risk_level_for_dependency(dep, ctx) == RISK_ACTION


def test_lgpl_distributed_without_modifications_is_review():
    ctx = ProductContext(use_case="Distributed", modifications_expected=False)
    dep = dep_with_license("LGPL-2.1-only")
    assert risk_level_for_dependency(dep, ctx) == RISK_REVIEW


def test_safety_critical_triggers_nis2_reference(safety_critical_ai_context):
    assessor = ComplianceAssessor()
    report = assessor.assess_dependencies([dep_with_license("MIT")], safety_critical_ai_context)
    assert any("NIS2" in ref for ref in report.regulatory_references)


def test_risk_summary_counts_are_accurate(distributed_context):
    deps = [
        dep_with_license("MIT", name="a"),
        dep_with_license("MIT", name="b"),
        dep_with_license("GPL-3.0-only", name="c"),
        unknown_dep(name="d"),
    ]
    report = ComplianceAssessor().assess_dependencies(deps, distributed_context)
    assert report.risk_summary[RISK_SAFE] == 2
    assert report.risk_summary[RISK_ACTION] == 2  # GPL+Distributed and Unknown
    assert report.risk_summary[RISK_REVIEW] == 0


def test_action_required_items_populated_for_action_risk(distributed_context):
    deps = [dep_with_license("GPL-3.0-only", name="gpl-lib")]
    report = ComplianceAssessor().assess_dependencies(deps, distributed_context)
    assert len(report.actions_required) == 1
    assert "gpl-lib" in report.actions_required[0]


def test_no_actions_required_when_all_safe(internal_context):
    deps = [dep_with_license("MIT"), dep_with_license("Apache-2.0")]
    report = ComplianceAssessor().assess_dependencies(deps, internal_context)
    assert report.actions_required == []


def test_report_carries_product_name_from_context():
    ctx = ProductContext(product_name="My Product", use_case="Internal")
    report = ComplianceAssessor().assess_dependencies([], ctx)
    assert report.product_name == "My Product"
