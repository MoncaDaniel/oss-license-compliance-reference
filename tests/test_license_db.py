"""Tests for the SPDX-derived license database."""

from oss_compliance.license_db import all_known_spdx_ids, get_license


def test_lookup_mit_correctly():
    lic = get_license("MIT")
    assert lic is not None
    assert lic.spdx_id == "MIT"
    assert lic.risk_level_base == "Permissive"
    assert lic.source_disclosure_requirement is False


def test_lookup_gpl_v2_correctly():
    lic = get_license("GPL-2.0-only")
    assert lic is not None
    assert lic.risk_level_base == "Strong Copyleft"
    assert lic.source_disclosure_requirement is True
    assert lic.triggers_on_distribution is True
    assert lic.triggers_on_network_use is False


def test_lookup_apache_2_correctly():
    lic = get_license("Apache-2.0")
    assert lic is not None
    assert lic.risk_level_base == "Permissive"
    assert lic.commercial_use_allowed is True


def test_handle_unknown_license():
    assert get_license("TotallyMadeUpLicense-9000") is None
    assert get_license("") is None
    assert get_license(None) is None


def test_distinguish_gpl_v2_vs_v3():
    v2 = get_license("GPL-2.0-only")
    v3 = get_license("GPL-3.0-only")
    assert v2.spdx_id != v3.spdx_id
    assert "patent" in " ".join(v3.key_restrictions).lower()
    assert "patent" not in " ".join(v2.key_restrictions).lower()


def test_distinguish_lgpl_vs_agpl():
    lgpl = get_license("LGPL-3.0-only")
    agpl = get_license("AGPL-3.0-only")
    assert lgpl.risk_level_base == "Weak Copyleft"
    assert agpl.risk_level_base == "Network Copyleft"
    assert lgpl.triggers_on_network_use is False
    assert agpl.triggers_on_network_use is True


def test_alias_lookup_is_case_insensitive():
    assert get_license("apache 2.0").spdx_id == "Apache-2.0"
    assert get_license("gplv3").spdx_id == "GPL-3.0-only"
    assert get_license("AGPLv3").spdx_id == "AGPL-3.0-only"


def test_all_known_spdx_ids_includes_core_licenses():
    ids = all_known_spdx_ids()
    for expected in ("MIT", "Apache-2.0", "GPL-2.0-only", "GPL-3.0-only", "AGPL-3.0-only"):
        assert expected in ids
