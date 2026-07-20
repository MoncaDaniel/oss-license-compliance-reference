"""Tests for PDF report generation."""

import os

import pytest

from oss_compliance.assessor import ComplianceAssessor
from oss_compliance.license_db import get_license
from oss_compliance.models import Dependency, ProductContext
from oss_compliance.reporter import PDFReporter

reportlab = pytest.importorskip("reportlab")


def make_report():
    context = ProductContext(
        product_name="Test Product",
        use_case="Distributed",
        data_types=["Industrial/operational data"],
        target_markets=["EU"],
        is_safety_critical=True,
        has_ai=True,
    )
    deps = [
        Dependency(name="requests", version="2.31.0", license_id="Apache-2.0", license=get_license("Apache-2.0")),
        Dependency(name="gpl-lib", version="1.0", license_id="GPL-3.0-only", license=get_license("GPL-3.0-only")),
        Dependency(name="mystery-lib", version="1.0", license_id="Unknown", license=None),
    ]
    return ComplianceAssessor().assess_dependencies(deps, context)


def test_pdf_file_is_generated(tmp_path):
    report = make_report()
    output_path = str(tmp_path / "report.pdf")
    result = PDFReporter().generate_report(report, output_path)
    assert result == output_path
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
    with open(output_path, "rb") as f:
        assert f.read(5) == b"%PDF-"


def test_disclaimer_is_present_in_report_object():
    report = make_report()
    assert "qualified legal counsel" in report.disclaimer.lower()


def test_product_summary_is_accurate(tmp_path):
    report = make_report()
    PDFReporter().generate_report(report, str(tmp_path / "report.pdf"))
    assert report.product_name == "Test Product"
    assert report.context.use_case == "Distributed"


def test_risk_table_is_populated(tmp_path):
    report = make_report()
    PDFReporter().generate_report(report, str(tmp_path / "report.pdf"))
    assert sum(report.risk_summary.values()) == len(report.dependencies)


def test_actions_required_are_listed(tmp_path):
    report = make_report()
    PDFReporter().generate_report(report, str(tmp_path / "report.pdf"))
    assert len(report.actions_required) >= 1  # GPL+Distributed and Unknown both trigger ACTION
