"""A small, curated SPDX-derived license database.

This is not the full ~700-entry SPDX list -- it covers the licenses teams
actually hit in practice (permissive + the copyleft family), each with the
fields the assessor needs to reason about context-dependent risk. Extend
`_LICENSES` if a scan surfaces something not covered; unresolved licenses
fall back to `None` (treated as "Unknown" -- see assessor.py), which is a
deliberate 🔴 signal rather than a silent guess.

IMPORTANT (Anomaly #5 -- terminology accuracy): licenses are described by
what they actually require (e.g. "source code must be provided on
distribution"), not folk terms like "GPL contamination" or "viral license".
"""

from typing import Dict, Optional

from .models import License

_LICENSES: Dict[str, License] = {
    "MIT": License(
        name="MIT License",
        spdx_id="MIT",
        summary="Highly permissive; requires only that the copyright notice and "
        "license text be retained in copies.",
        reference_url="https://spdx.org/licenses/MIT.html",
        risk_level_base="Permissive",
        source_disclosure_requirement=False,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=["Must retain copyright notice and license text"],
    ),
    "Apache-2.0": License(
        name="Apache License 2.0",
        spdx_id="Apache-2.0",
        summary="Permissive; includes an express patent grant and a patent "
        "retaliation clause.",
        reference_url="https://spdx.org/licenses/Apache-2.0.html",
        risk_level_base="Permissive",
        source_disclosure_requirement=False,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=[
            "Must retain copyright/license notice",
            "Must state significant changes made to the file",
            "Patent grant terminates if you sue a contributor over patent infringement",
        ],
    ),
    "BSD-2-Clause": License(
        name="BSD 2-Clause License",
        spdx_id="BSD-2-Clause",
        summary="Permissive; functionally similar to MIT.",
        reference_url="https://spdx.org/licenses/BSD-2-Clause.html",
        risk_level_base="Permissive",
        source_disclosure_requirement=False,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=["Must retain copyright notice and license text"],
    ),
    "BSD-3-Clause": License(
        name="BSD 3-Clause License",
        spdx_id="BSD-3-Clause",
        summary="Permissive; adds a non-endorsement clause over BSD-2-Clause.",
        reference_url="https://spdx.org/licenses/BSD-3-Clause.html",
        risk_level_base="Permissive",
        source_disclosure_requirement=False,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=[
            "Must retain copyright notice and license text",
            "May not use contributors' names to endorse derived products without permission",
        ],
    ),
    "ISC": License(
        name="ISC License",
        spdx_id="ISC",
        summary="Permissive; functionally equivalent to MIT/BSD-2-Clause with "
        "simplified wording.",
        reference_url="https://spdx.org/licenses/ISC.html",
        risk_level_base="Permissive",
        source_disclosure_requirement=False,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=["Must retain copyright notice and license text"],
    ),
    "Unlicense": License(
        name="The Unlicense",
        spdx_id="Unlicense",
        summary="Public-domain dedication; effectively no restrictions.",
        reference_url="https://spdx.org/licenses/Unlicense.html",
        risk_level_base="Permissive",
        source_disclosure_requirement=False,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=[],
    ),
    "MPL-2.0": License(
        name="Mozilla Public License 2.0",
        spdx_id="MPL-2.0",
        summary="Weak, file-level copyleft: modifications to MPL-licensed files "
        "must stay under MPL-2.0 if distributed, but the license does not "
        "extend to separate files in a larger work.",
        reference_url="https://spdx.org/licenses/MPL-2.0.html",
        risk_level_base="Weak Copyleft",
        source_disclosure_requirement=True,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=[
            "Modified MPL-licensed files must remain under MPL-2.0 if distributed",
            "Can be combined with proprietary code, provided combination is in separate files",
        ],
        triggers_on_distribution=True,
    ),
    "LGPL-2.1-only": License(
        name="GNU Lesser General Public License v2.1 only",
        spdx_id="LGPL-2.1-only",
        summary="Weak copyleft: permits linking from proprietary software; "
        "modifications to the LGPL-licensed library itself must be shared if "
        "distributed, and users must be able to relink a different version of "
        "the library.",
        reference_url="https://spdx.org/licenses/LGPL-2.1-only.html",
        risk_level_base="Weak Copyleft",
        source_disclosure_requirement=True,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=[
            "Modifications to the library itself must be shared if distributed",
            "Must allow relinking against a modified/updated version of the library",
            "Does not require disclosure of the proprietary application linking to it",
        ],
        triggers_on_distribution=True,
    ),
    "LGPL-3.0-only": License(
        name="GNU Lesser General Public License v3.0 only",
        spdx_id="LGPL-3.0-only",
        summary="Weak copyleft, LGPLv3 -- same linking model as LGPL-2.1 with "
        "GPLv3's patent and anti-tivoization provisions layered in.",
        reference_url="https://spdx.org/licenses/LGPL-3.0-only.html",
        risk_level_base="Weak Copyleft",
        source_disclosure_requirement=True,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=[
            "Modifications to the library itself must be shared if distributed",
            "Must allow relinking against a modified/updated version of the library",
            "Includes GPLv3 patent grant and anti-tivoization provisions",
        ],
        triggers_on_distribution=True,
    ),
    "GPL-2.0-only": License(
        name="GNU General Public License v2.0 only",
        spdx_id="GPL-2.0-only",
        summary="Strong copyleft: distributing a binary built from GPL-2.0 code "
        "requires providing the corresponding source code under GPL-2.0. Not "
        "triggered by purely internal use, and not triggered by running the "
        "software as a network service without distributing it.",
        reference_url="https://spdx.org/licenses/GPL-2.0-only.html",
        risk_level_base="Strong Copyleft",
        source_disclosure_requirement=True,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=[
            "Source code must be provided upon distribution of binaries",
            "Derivative/combined works distributed must remain under GPL-2.0",
        ],
        triggers_on_distribution=True,
    ),
    "GPL-3.0-only": License(
        name="GNU General Public License v3.0 only",
        spdx_id="GPL-3.0-only",
        summary="Strong copyleft, GPLv3 -- same distribution-triggered source "
        "disclosure as GPL-2.0, plus an explicit patent grant/retaliation clause "
        "and an anti-tivoization provision (user must be able to install "
        "modified software on the hardware it ships with, where applicable). "
        "Still not triggered by SaaS/network use alone -- that is what AGPL-3.0 "
        "is for.",
        reference_url="https://spdx.org/licenses/GPL-3.0-only.html",
        risk_level_base="Strong Copyleft",
        source_disclosure_requirement=True,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=[
            "Source code must be provided upon distribution of binaries",
            "Derivative/combined works distributed must remain under GPL-3.0",
            "Explicit patent grant with patent-litigation retaliation clause",
            "Anti-tivoization: must allow installation of modified versions where applicable",
        ],
        triggers_on_distribution=True,
    ),
    "AGPL-3.0-only": License(
        name="GNU Affero General Public License v3.0 only",
        spdx_id="AGPL-3.0-only",
        summary="Network copyleft: closes the so-called 'SaaS loophole' in "
        "GPL-3.0. Source code must be made available to any user who interacts "
        "with the software over a network, even if no binary is ever "
        "distributed (AGPL-3.0 Section 13).",
        reference_url="https://spdx.org/licenses/AGPL-3.0-only.html",
        risk_level_base="Network Copyleft",
        source_disclosure_requirement=True,
        modifications_allowed=True,
        commercial_use_allowed=True,
        key_restrictions=[
            "Source code must be offered to users interacting with the software over a network",
            "Applies to SaaS/hosted deployment, not just traditional distribution",
            "Derivative/combined works must remain under AGPL-3.0",
        ],
        triggers_on_distribution=True,
        triggers_on_network_use=True,
    ),
}

# Common aliases seen in the wild (package manager metadata, human-written
# license fields, older SPDX expression styles) mapped to a canonical key
# above. Lookups are case-insensitive.
_ALIASES: Dict[str, str] = {
    "APACHE 2.0": "Apache-2.0",
    "APACHE-2.0": "Apache-2.0",
    "APACHE2": "Apache-2.0",
    "APACHE LICENSE 2.0": "Apache-2.0",
    "BSD": "BSD-3-Clause",
    "BSD-3": "BSD-3-Clause",
    "BSD-2": "BSD-2-Clause",
    "GPL": "GPL-3.0-only",  # bare "GPL" most often means the latest major version in practice
    "GPL V2": "GPL-2.0-only",
    "GPLV2": "GPL-2.0-only",
    "GPL-2.0": "GPL-2.0-only",
    "GPL-2.0+": "GPL-2.0-only",
    "GPL2": "GPL-2.0-only",
    "GPL V3": "GPL-3.0-only",
    "GPLV3": "GPL-3.0-only",
    "GPL-3.0": "GPL-3.0-only",
    "GPL-3.0+": "GPL-3.0-only",
    "GPL3": "GPL-3.0-only",
    "LGPL": "LGPL-3.0-only",
    "LGPL-2.1": "LGPL-2.1-only",
    "LGPLV2.1": "LGPL-2.1-only",
    "LGPL-3.0": "LGPL-3.0-only",
    "LGPLV3": "LGPL-3.0-only",
    "AGPL": "AGPL-3.0-only",
    "AGPL-3.0": "AGPL-3.0-only",
    "AGPLV3": "AGPL-3.0-only",
    "AFFERO GPL": "AGPL-3.0-only",
    "MOZILLA PUBLIC LICENSE 2.0": "MPL-2.0",
    "UNLICENSE": "Unlicense",
    "THE UNLICENSE": "Unlicense",
}


def get_license(identifier: str) -> Optional[License]:
    """Look up a License by SPDX id or common alias. Returns None if the
    identifier isn't recognized -- callers should treat that as "Unknown",
    not silently assume permissive."""
    if not identifier:
        return None

    if identifier in _LICENSES:
        return _LICENSES[identifier]

    key = identifier.strip().upper()
    canonical = _ALIASES.get(key)
    if canonical:
        return _LICENSES.get(canonical)

    # Case-insensitive direct match against canonical SPDX ids.
    for spdx_id, lic in _LICENSES.items():
        if spdx_id.upper() == key:
            return lic

    return None


def all_known_spdx_ids():
    return list(_LICENSES.keys())
