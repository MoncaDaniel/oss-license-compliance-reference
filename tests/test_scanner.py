"""Tests for dependency manifest parsing."""

import json

from oss_compliance.scanner import DependencyScanner


def write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content)
    return str(path)


def test_parse_requirements_txt_correctly(tmp_path):
    path = write(
        tmp_path,
        "requirements.txt",
        "requests==2.31.0\nflask==2.3.0\n",
    )
    deps = DependencyScanner().scan_requirements_file(path)
    names = {d.name for d in deps}
    assert names == {"requests", "flask"}


def test_parse_package_json_correctly(tmp_path):
    content = json.dumps(
        {
            "dependencies": {"express": "^4.18.0", "lodash": "~4.17.21"},
            "devDependencies": {"eslint": "^8.0.0"},
        }
    )
    path = write(tmp_path, "package.json", content)
    deps = DependencyScanner().scan_package_json(path)
    names = {d.name for d in deps}
    assert names == {"express", "lodash", "eslint"}


def test_parse_cyclonedx_sbom_correctly(tmp_path):
    content = json.dumps(
        {
            "bomFormat": "CycloneDX",
            "components": [
                {
                    "name": "vendor-lib",
                    "version": "3.2.1",
                    "licenses": [{"license": {"id": "MIT"}}],
                }
            ],
        }
    )
    path = write(tmp_path, "sbom.json", content)
    deps = DependencyScanner().scan_sbom_file(path)
    assert len(deps) == 1
    assert deps[0].name == "vendor-lib"
    assert deps[0].version == "3.2.1"
    assert deps[0].license_id == "MIT"
    assert deps[0].license is not None


def test_handle_missing_requirements_file_gracefully(tmp_path):
    missing = str(tmp_path / "does_not_exist.txt")
    deps = DependencyScanner().scan_requirements_file(missing)
    assert deps == []


def test_handle_malformed_package_json_gracefully(tmp_path):
    path = write(tmp_path, "package.json", "{not valid json")
    deps = DependencyScanner().scan_package_json(path)
    assert deps == []


def test_handle_malformed_sbom_gracefully(tmp_path):
    path = write(tmp_path, "sbom.json", "{not valid json")
    deps = DependencyScanner().scan_sbom_file(path)
    assert deps == []


def test_extract_pinned_version_accurately(tmp_path):
    path = write(tmp_path, "requirements.txt", "numpy==1.26.4\n")
    deps = DependencyScanner().scan_requirements_file(path)
    assert deps[0].version == "1.26.4"


def test_unpinned_requirement_marked_unspecified(tmp_path):
    path = write(tmp_path, "requirements.txt", "pandas>=2.0\n")
    deps = DependencyScanner().scan_requirements_file(path)
    assert deps[0].name == "pandas"
    assert deps[0].version == "unspecified"


def test_requirements_txt_handles_comments_and_blank_lines(tmp_path):
    content = "\n# a comment\nrequests==2.31.0\n\n   \n# another comment\nflask==2.3.0\n"
    path = write(tmp_path, "requirements.txt", content)
    deps = DependencyScanner().scan_requirements_file(path)
    assert {d.name for d in deps} == {"requests", "flask"}


def test_requirements_txt_skips_option_lines(tmp_path):
    content = "-r base.txt\n--index-url https://example.org/simple\nrequests==2.31.0\n"
    path = write(tmp_path, "requirements.txt", content)
    deps = DependencyScanner().scan_requirements_file(path)
    assert {d.name for d in deps} == {"requests"}


def test_requirements_txt_skips_vcs_urls(tmp_path):
    content = "git+https://github.com/example/lib.git@main#egg=lib\nrequests==2.31.0\n"
    path = write(tmp_path, "requirements.txt", content)
    deps = DependencyScanner().scan_requirements_file(path)
    assert {d.name for d in deps} == {"requests"}


def test_unknown_package_resolves_to_unknown_license(tmp_path):
    path = write(tmp_path, "requirements.txt", "some-totally-obscure-package==1.0\n")
    deps = DependencyScanner().scan_requirements_file(path)
    assert deps[0].license is None
    assert deps[0].license_id == "Unknown"


def test_sbom_component_without_license_resolves_to_unknown(tmp_path):
    content = json.dumps({"components": [{"name": "mystery-lib", "version": "1.0"}]})
    path = write(tmp_path, "sbom.json", content)
    deps = DependencyScanner().scan_sbom_file(path)
    assert deps[0].license is None
    assert deps[0].license_id == "Unknown"
