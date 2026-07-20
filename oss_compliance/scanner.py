"""Dependency scanners: requirements.txt, package.json, CycloneDX SBOM.

Scope note (Anomaly #1): this scans DIRECT dependencies as declared in the
manifest/SBOM handed to it. It does not resolve transitive dependency trees
-- a requirements.txt with 50 direct entries commonly implies 200+ installed
packages once transitive dependencies are included, and resolving that
reliably requires an actual package-manager install step (or a lockfile),
which is out of scope here. This limitation is stated in every generated
report, not just this docstring.

Offline-first (per project requirement: no external service dependency to
run a scan): license lookups for requirements.txt/package.json go through a
small curated offline dataset of common packages. SBOM files already carry
vendor-declared license data and don't need lookup at all. An optional
`http_get` callable can be injected into DependencyScanner for a future
online lookup path (e.g. PyPI/npm registry APIs) -- tests inject a fake
rather than hitting the network.
"""

import json
import re
from typing import Callable, List, Optional

from .license_db import get_license
from .models import Dependency, License

# A small, deliberately non-exhaustive offline dataset covering commonly
# seen packages, so a scan works without any network access. Anything not
# listed here resolves to an Unknown license (dependency.license is None),
# which is the correct, honest outcome -- not a silent guess.
_OFFLINE_PACKAGE_LICENSES = {
    # Python / PyPI
    "requests": "Apache-2.0",
    "flask": "BSD-3-Clause",
    "django": "BSD-3-Clause",
    "numpy": "BSD-3-Clause",
    "pandas": "BSD-3-Clause",
    "pytest": "MIT",
    "click": "BSD-3-Clause",
    "pyyaml": "MIT",
    "jinja2": "BSD-3-Clause",
    "cryptography": "Apache-2.0",
    "psycopg2": "LGPL-3.0-only",
    "pillow": "MIT",
    "sqlalchemy": "MIT",
    "gunicorn": "MIT",
    "celery": "BSD-3-Clause",
    "reportlab": "BSD-3-Clause",
    "readline": "GPL-3.0-only",
    "mysqlclient": "GPL-2.0-only",
    "pyqt5": "GPL-3.0-only",
    # Node.js / npm
    "express": "MIT",
    "lodash": "MIT",
    "react": "MIT",
    "vue": "MIT",
    "axios": "MIT",
    "chalk": "MIT",
    "commander": "MIT",
    "moment": "MIT",
    "webpack": "MIT",
    "eslint": "MIT",
    "typescript": "Apache-2.0",
    "readline-sync": "MIT",
    "gpl-sample-lib": "GPL-3.0-only",
    "agpl-sample-lib": "AGPL-3.0-only",
}

_REQUIREMENTS_LINE_RE = re.compile(
    r"^\s*([A-Za-z0-9_.\-]+)\s*(==|>=|<=|~=|!=|>|<)?\s*([A-Za-z0-9.\-*]+)?"
)


class DependencyScanner:
    """Parses dependency manifests into Dependency objects with resolved
    licenses where possible."""

    def __init__(self, http_get: Optional[Callable[[str], dict]] = None):
        # Reserved for a future online lookup path; unused by default so the
        # tool works fully offline.
        self._http_get = http_get

    def scan_requirements_file(self, file_path: str) -> List[Dependency]:
        """Parse a Python requirements.txt file into Dependency objects.

        Handles comments, blank lines, `-r`/`-e`/`--index-url` option lines
        (skipped -- not a package), and version specifiers (==, >=, ~=, etc).
        Packages without a pinned exact version get version="unspecified".
        """
        dependencies: List[Dependency] = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except (FileNotFoundError, OSError):
            return dependencies

        for raw_line in lines:
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            if line.startswith("-") or line.startswith("--"):
                continue  # option lines like -r other.txt, -e ., --index-url ...
            if line.startswith("git+") or "://" in line:
                continue  # VCS/URL requirements: no reliable name/version to extract

            match = _REQUIREMENTS_LINE_RE.match(line)
            if not match:
                continue
            name, operator, version = match.groups()
            if not name:
                continue

            resolved_version = version if (operator == "==" and version) else "unspecified"
            dependencies.append(self._build_dependency(name, resolved_version, source="PyPI"))

        return dependencies

    def scan_package_json(self, file_path: str) -> List[Dependency]:
        """Parse a Node.js package.json's `dependencies` and
        `devDependencies` into Dependency objects. Version ranges (^, ~,
        etc.) are kept as declared rather than resolved to an exact
        installed version, since that requires a lockfile."""
        dependencies: List[Dependency] = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return dependencies

        for section in ("dependencies", "devDependencies"):
            for name, version_range in (data.get(section) or {}).items():
                dependencies.append(
                    self._build_dependency(name, str(version_range), source="npm")
                )

        return dependencies

    def scan_sbom_file(self, file_path: str) -> List[Dependency]:
        """Parse a CycloneDX SBOM (JSON) into Dependency objects. SBOM
        components carry vendor-declared license data directly, so no
        offline-dataset lookup is needed here."""
        dependencies: List[Dependency] = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return dependencies

        for component in data.get("components", []):
            name = component.get("name", "unknown")
            version = component.get("version", "unspecified")
            spdx_id = self._extract_sbom_license_id(component)
            license_obj = get_license(spdx_id) if spdx_id else None
            dependencies.append(
                Dependency(
                    name=name,
                    version=version,
                    license_id=spdx_id or "Unknown",
                    license=license_obj,
                    source="SBOM",
                )
            )

        return dependencies

    def lookup_license(self, package_name: str, version: str) -> Optional[License]:
        """Look up the license for a package. Checks the offline curated
        dataset first; returns None (Unknown) if not found. `version` is
        accepted for interface symmetry with a future version-specific
        online lookup -- the offline dataset is not currently version-aware.
        """
        spdx_id = _OFFLINE_PACKAGE_LICENSES.get(package_name.lower())
        if not spdx_id:
            return None
        return get_license(spdx_id)

    def _build_dependency(self, name: str, version: str, source: str) -> Dependency:
        license_obj = self.lookup_license(name, version)
        return Dependency(
            name=name,
            version=version,
            license_id=license_obj.spdx_id if license_obj else "Unknown",
            license=license_obj,
            source=source,
        )

    @staticmethod
    def _extract_sbom_license_id(component: dict) -> Optional[str]:
        licenses = component.get("licenses") or []
        for entry in licenses:
            license_info = entry.get("license") or {}
            if license_info.get("id"):
                return license_info["id"]
            if license_info.get("name"):
                return license_info["name"]
            if entry.get("expression"):
                return entry["expression"]
        return None
