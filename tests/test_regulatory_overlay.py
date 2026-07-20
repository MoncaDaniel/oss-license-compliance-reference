"""Tests for the regulatory reference overlay -- these also serve as
regression tests against the citation/date/penalty errors identified during
review (wrong CRA/Data Act regulation numbers, wrong Data Act date, flat
6% AI Act penalty)."""

from oss_compliance.license_db import get_license
from oss_compliance.models import ProductContext
from oss_compliance.regulatory_overlay import RegulatoryOverlay


def test_cra_referenced_for_digital_products():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Embedded")
    refs = overlay.get_applicable_regulations(ctx)
    assert any("CRA" in r for r in refs)


def test_cra_citation_is_correct_not_2599():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="SaaS")
    refs = " ".join(overlay.get_applicable_regulations(ctx))
    assert "2024/2847" in refs
    assert "2024/2599" not in refs


def test_nis2_referenced_for_safety_critical():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Internal", is_safety_critical=True)
    refs = overlay.get_applicable_regulations(ctx)
    assert any("NIS2" in r for r in refs)


def test_data_act_referenced_for_saas():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="SaaS")
    refs = overlay.get_applicable_regulations(ctx)
    assert any("Data Act" in r for r in refs)


def test_data_act_citation_and_date_are_correct():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="SaaS")
    refs = " ".join(overlay.get_applicable_regulations(ctx))
    assert "2023/2854" in refs
    assert "2024/2897" not in refs
    assert "12 Sept 2025" in refs


def test_ai_act_referenced_if_has_ai():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Internal", has_ai=True)
    refs = overlay.get_applicable_regulations(ctx)
    assert any("AI Act" in r for r in refs)


def test_ai_act_penalties_are_tiered_not_flat_6_percent():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Internal", has_ai=True)
    refs = " ".join(overlay.get_applicable_regulations(ctx))
    assert "7%" in refs
    assert "3%" in refs
    assert "1%" in refs


def test_no_regulations_for_purely_internal_non_ai_non_critical_product():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Internal")
    refs = overlay.get_applicable_regulations(ctx)
    assert refs == []


def test_gpl_distributed_explains_source_disclosure_requirement():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Distributed")
    lic = get_license("GPL-3.0-only")
    text = overlay.get_license_implications(lic, ctx)
    assert "source code" in text.lower()
    assert "distribut" in text.lower()


def test_agpl_saas_explains_network_use_trigger():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="SaaS")
    lic = get_license("AGPL-3.0-only")
    text = overlay.get_license_implications(lic, ctx)
    assert "network" in text.lower()


def test_unknown_license_implication_flags_investigation():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Internal")
    text = overlay.get_license_implications(None, ctx)
    assert "investigat" in text.lower()


def test_gpl_embedded_explains_hardware_distribution():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Embedded")
    lic = get_license("GPL-2.0-only")
    text = overlay.get_license_implications(lic, ctx)
    assert "hardware" in text.lower()
    assert "distribution" in text.lower()


def test_gpl_saas_explains_no_automatic_trigger():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="SaaS")
    lic = get_license("GPL-3.0-only")
    text = overlay.get_license_implications(lic, ctx)
    assert "agpl" in text.lower()
    assert "does not, by itself, trigger" in text.lower()


def test_gpl_internal_explains_no_restriction():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Internal")
    lic = get_license("GPL-3.0-only")
    text = overlay.get_license_implications(lic, ctx)
    assert "no restriction" in text.lower()


def test_agpl_internal_explains_network_ambiguity():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Internal")
    lic = get_license("AGPL-3.0-only")
    text = overlay.get_license_implications(lic, ctx)
    assert "internal" in text.lower()
    assert "network" in text.lower()


def test_permissive_license_implication_mentions_no_disclosure():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Distributed")
    lic = get_license("MIT")
    text = overlay.get_license_implications(lic, ctx)
    assert "no source disclosure requirement" in text.lower()


def test_weak_copyleft_internal_not_triggered():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Internal")
    lic = get_license("LGPL-2.1-only")
    text = overlay.get_license_implications(lic, ctx)
    assert "do not apply" in text.lower()


def test_weak_copyleft_distributed_with_modifications():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Distributed", modifications_expected=True)
    lic = get_license("LGPL-2.1-only")
    text = overlay.get_license_implications(lic, ctx)
    assert "relink" in text.lower()


def test_weak_copyleft_distributed_without_modifications():
    overlay = RegulatoryOverlay()
    ctx = ProductContext(use_case="Distributed", modifications_expected=False)
    lic = get_license("MPL-2.0")
    text = overlay.get_license_implications(lic, ctx)
    assert "confirm no undocumented modifications" in text.lower()
