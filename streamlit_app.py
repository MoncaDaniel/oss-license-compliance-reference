"""Interactive demo for the OSS License Compliance Reference tool.

This file is a thin UI layer only -- all scanning/assessment/reporting
logic lives in oss_compliance/ and is exercised here exactly as a library
consumer would use it. See DISCLAIMER.md for what this tool is and isn't.
"""

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from i18n import LANGUAGES, get_translator
from oss_compliance.assessor import ComplianceAssessor
from oss_compliance.models import RISK_ACTION, RISK_REVIEW, RISK_SAFE, ProductContext
from oss_compliance.reporter import PDFReporter
from oss_compliance.scanner import DependencyScanner

REPO_URL = "https://github.com/MoncaDaniel/oss-license-compliance-reference"
EXAMPLES_DIR = Path(__file__).parent / "examples"

st.set_page_config(page_title="OSS License Compliance Reference", page_icon="📋", layout="wide")

# ---------------------------------------------------------------------------
# Language selector (sidebar) -- drives every label via t()
# ---------------------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "en"

with st.sidebar:
    lang_code = st.selectbox(
        "🌐 " + LANGUAGES[st.session_state.lang],
        options=list(LANGUAGES.keys()),
        format_func=lambda code: LANGUAGES[code],
        index=list(LANGUAGES.keys()).index(st.session_state.lang),
    )
    st.session_state.lang = lang_code

t = get_translator(st.session_state.lang)

with st.sidebar:
    st.markdown(f"[{t('source_link')}]({REPO_URL})")

# ---------------------------------------------------------------------------
# Header + disclaimer
# ---------------------------------------------------------------------------
st.title(t("app_title"))
st.caption(t("app_subtitle"))
st.warning(f"⚠️ {t('disclaimer_banner')}")

# ---------------------------------------------------------------------------
# Step 1: get dependencies (sample data or upload)
# ---------------------------------------------------------------------------
st.header(t("step1_header"))

scanner = DependencyScanner()
deps = None

col_sample, col_upload = st.columns([1, 2])

with col_sample:
    if st.button(t("try_sample_button"), type="primary", width="stretch"):
        st.session_state.use_sample = True
    st.caption(t("try_sample_caption"))

with col_upload:
    st.markdown(f"**{t('or_divider')}**")
    file_type = st.radio(
        t("file_type_label"),
        options=["requirements", "package_json", "sbom"],
        format_func=lambda k: {
            "requirements": t("file_type_requirements"),
            "package_json": t("file_type_package_json"),
            "sbom": t("file_type_sbom"),
        }[k],
        horizontal=True,
    )
    uploaded_file = st.file_uploader(t("upload_label"), help=t("upload_help"))
    if uploaded_file is not None:
        st.session_state.use_sample = False

if st.session_state.get("use_sample"):
    deps = (
        scanner.scan_requirements_file(str(EXAMPLES_DIR / "sample_requirements.txt"))
        + scanner.scan_package_json(str(EXAMPLES_DIR / "sample_package.json"))
        + scanner.scan_sbom_file(str(EXAMPLES_DIR / "sample_sbom.json"))
    )
elif uploaded_file is not None:
    suffix = Path(uploaded_file.name).suffix or ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    try:
        if file_type == "requirements":
            deps = scanner.scan_requirements_file(tmp_path)
        elif file_type == "package_json":
            deps = scanner.scan_package_json(tmp_path)
        else:
            deps = scanner.scan_sbom_file(tmp_path)
    except Exception:
        st.error(t("parse_error"))
        deps = None
    finally:
        Path(tmp_path).unlink(missing_ok=True)

if deps is not None and len(deps) == 0:
    st.warning(t("no_dependencies_warning"))
    deps = None

if deps:
    st.success(f"✓ {t('deps_loaded').format(n=len(deps))}")

# ---------------------------------------------------------------------------
# Step 2: business context
# ---------------------------------------------------------------------------
st.header(t("step2_header"))

c1, c2 = st.columns(2)
with c1:
    product_name = st.text_input(t("product_name_label"), placeholder=t("product_name_placeholder"))
    use_case_key = st.selectbox(
        t("use_case_label"),
        options=["Internal", "Embedded", "SaaS", "Distributed"],
        format_func=lambda k: {
            "Internal": t("use_case_internal"),
            "Embedded": t("use_case_embedded"),
            "SaaS": t("use_case_saas"),
            "Distributed": t("use_case_distributed"),
        }[k],
    )
    target_markets = st.multiselect(t("target_markets_label"), options=["EU", "US", "UK", "Asia", "Other"], default=["EU"])

with c2:
    data_type_options = st.multiselect(
        t("data_types_label"),
        options=["industrial", "customer"],
        format_func=lambda k: {"industrial": t("data_type_industrial"), "customer": t("data_type_customer")}[k],
    )
    is_safety_critical = st.checkbox(t("safety_critical_label"))
    has_ai = st.checkbox(t("has_ai_label"))
    modifications_expected = st.checkbox(t("modifications_label"))

data_types = []
if "industrial" in data_type_options:
    data_types.append("Industrial/operational data")
if "customer" in data_type_options:
    data_types.append("Customer data (GDPR-protected)")

context = ProductContext(
    product_name=product_name or "Untitled product",
    use_case=use_case_key,
    data_types=data_types,
    target_markets=target_markets,
    is_safety_critical=is_safety_critical,
    has_ai=has_ai,
    modifications_expected=modifications_expected,
)

# ---------------------------------------------------------------------------
# Analyze
# ---------------------------------------------------------------------------
analyze_clicked = st.button(t("analyze_button"), type="primary", disabled=not deps)

if analyze_clicked and deps:
    report = ComplianceAssessor().assess_dependencies(deps, context)

    st.header(t("results_header"))

    st.subheader(t("risk_summary_header"))
    m1, m2, m3 = st.columns(3)
    m1.metric(f"🟢 {t('risk_safe')}", report.risk_summary.get(RISK_SAFE, 0))
    m2.metric(f"🟡 {t('risk_review')}", report.risk_summary.get(RISK_REVIEW, 0))
    m3.metric(f"🔴 {t('risk_action')}", report.risk_summary.get(RISK_ACTION, 0))

    st.subheader(t("dependencies_header"))
    rows = [
        {
            t("col_library"): d.name,
            t("col_version"): d.version,
            t("col_license"): d.license.name if d.license else "Unknown",
            t("col_risk"): d.risk_level_for_context(context),
        }
        for d in report.dependencies
    ]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    st.caption(t("regulatory_text_note"))

    st.subheader(t("regulations_header"))
    if report.regulatory_references:
        for ref in report.regulatory_references:
            if ref.startswith("  "):
                st.markdown(f"  ↳ {ref.strip()}")
            else:
                st.markdown(f"**{ref}**")
    else:
        st.write(t("no_regulations"))

    st.subheader(t("actions_header"))
    if report.actions_required:
        for action in report.actions_required:
            st.markdown(f"- {action}")
    else:
        st.write(t("no_actions"))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_tmp:
        PDFReporter().generate_report(report, pdf_tmp.name)
        pdf_bytes = Path(pdf_tmp.name).read_bytes()
    Path(pdf_tmp.name).unlink(missing_ok=True)

    st.download_button(
        t("download_pdf_button"),
        data=pdf_bytes,
        file_name=f"{(product_name or 'compliance-report').replace(' ', '_')}.pdf",
        mime="application/pdf",
        type="primary",
    )

st.divider()
st.caption(t("footer_text"))
