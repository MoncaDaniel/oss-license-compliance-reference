"""Regulatory reference overlay: cross-references OSS findings against four
EU digital regulations (Anomaly #7). This module provides REFERENCES, not
legal interpretation -- it tells the user which regulations plausibly apply
and points at the relevant obligation, and leaves the "what do I do about
it" judgment to legal counsel.

Regulatory citations verified against EUR-Lex and legislative tracking
sources as of July 2026. Where a widely-circulated internal brief for this
project cited different regulation numbers/dates, the discrepancy and the
corrected figure are noted inline -- see each block below.
"""

from datetime import date

from .models import License, ProductContext

# ---------------------------------------------------------------------------
# Regulation reference constants.
#
# CORRECTED vs. common misstatements seen in internal drafts:
#   - CRA is Regulation (EU) 2024/2847 (NOT 2024/2599, which is not a real
#     CRA citation). It is also not simply "live since Sept 2024" -- see
#     CRA_NOTE below for the staggered applicability dates.
#   - EU Data Act is Regulation (EU) 2023/2854 (NOT 2024/2897). Its general
#     applicability began 12 Sept 2025, not "Sept 2026" -- the 2026 date is
#     a narrower, later obligation (see DATA_ACT_NOTE).
#   - AI Act penalties are tiered (up to 7% for prohibited practices, 3%
#     for high-risk/other obligations, 1% for misleading information) --
#     not a flat "6%".
# ---------------------------------------------------------------------------

CRA_ID = "Regulation (EU) 2024/2847 -- Cyber Resilience Act"
CRA_NOTE = (
    "Vulnerability/incident reporting obligations apply from 11 Sept 2026; "
    "essential requirements and conformity assessment apply from 11 Dec 2027. "
    "Not a single 'live since 2024' obligation."
)

NIS2_ID = "Directive (EU) 2022/2555 -- NIS2"
NIS2_NOTE = (
    "A directive, not a regulation -- binding only via each Member State's "
    "national transposition law (transposition deadline was 17 Oct 2024). "
    "Verify transposition status per jurisdiction."
)

DATA_ACT_ID = "Regulation (EU) 2023/2854 -- EU Data Act"
DATA_ACT_NOTE = (
    "General applicability (data access/portability rights) began 12 Sept "
    "2025. The connected-product 'access by design' obligation applies from "
    "12 Sept 2026 -- these are two different deadlines."
)

AI_ACT_ID = "Regulation (EU) 2024/1689 -- EU AI Act"
AI_ACT_NOTE = (
    "Prohibited practices apply since 2 Feb 2025. High-risk obligations were "
    "originally due 2 Aug 2026 (standalone, Annex III) / 2 Aug 2027 (embedded "
    "safety components, Annex I), but a May 2026 Digital Omnibus political "
    "agreement defers these to 2 Dec 2027 / 2 Aug 2028 respectively -- "
    "reconfirm formal adoption status before relying on either date. "
    "Penalties are tiered: up to EUR 35M/7% (prohibited practices), "
    "EUR 15M/3% (high-risk & most other obligations), EUR 7.5M/1% "
    "(misleading information) -- not a flat 6%."
)


class RegulatoryOverlay:
    """Provides regulatory context for open source findings. NOT legal
    interpretation -- reference material only."""

    def get_applicable_regulations(self, context: ProductContext) -> list:
        """Which regulations plausibly apply to this product context?
        This is a coarse screen for awareness, not a scope determination."""
        regs = []

        if context.use_case in ("Embedded", "SaaS", "Distributed"):
            regs.append(f"CRA: Cyber Resilience Act ({CRA_ID.split('--')[0].strip()})")
            regs.append("  -> Security-by-design and vulnerability management obligations")
            regs.append("  -> Components (including open source) must be documented (e.g. SBOM)")
            regs.append(f"  -> {CRA_NOTE}")

        if context.is_safety_critical:
            regs.append(f"NIS2: Network and Information Security Directive 2 ({NIS2_ID.split('--')[0].strip()})")
            regs.append("  -> Supply chain security requirement")
            regs.append("  -> Third-party components, including open source, are in scope of the risk assessment")
            regs.append(f"  -> {NIS2_NOTE}")

        if "Industrial/operational data" in context.data_types or context.use_case == "SaaS":
            regs.append(f"Data Act: EU Data Act ({DATA_ACT_ID.split('--')[0].strip()})")
            regs.append("  -> Data access and portability rights for industrial/machine data")
            regs.append(f"  -> {DATA_ACT_NOTE}")

        if context.has_ai:
            regs.append(f"AI Act: EU AI Act ({AI_ACT_ID.split('--')[0].strip()})")
            regs.append("  -> Risk-tier classification determines which obligations apply")
            regs.append("  -> High-risk systems require documentation, logging, human oversight")
            regs.append(f"  -> {AI_ACT_NOTE}")

        return regs

    def get_license_implications(self, license: License, context: ProductContext) -> str:
        """Plain-English explanation of why a specific license might need
        attention in this context. Terminology follows what the license
        actually requires (Anomaly #5) rather than folk terms."""
        if license is None:
            return (
                "No license could be resolved for this dependency. Its terms are "
                "unknown, which means neither permissions nor obligations can be "
                "confirmed -- treat as requiring investigation before use."
            )

        base = license.risk_level_base

        if base == "Permissive":
            return (
                f"{license.name} is permissive: no source disclosure requirement, "
                "modification and commercial use are allowed. Retain the required "
                "notice/attribution."
            )

        if base == "Network Copyleft":  # AGPL family
            if context.use_case in ("SaaS", "Distributed", "Embedded"):
                return (
                    f"{license.name} requires that source code be offered to any "
                    "user who interacts with the software over a network -- this is "
                    "what distinguishes AGPL from GPL, and it applies to SaaS/hosted "
                    "deployment even without distributing a binary."
                )
            return (
                f"{license.name}'s network-use trigger does not depend on 'internal' "
                "vs 'external' framing -- if any user interacts with a modified "
                "version over a network (including an internal one), the source "
                "offer obligation can still apply. Confirm actual network exposure "
                "before treating this as low risk."
            )

        if base == "Strong Copyleft":  # GPL family
            if context.use_case == "Distributed":
                return (
                    f"{license.name} requires that source code be provided to "
                    "recipients when you distribute a binary that includes or links "
                    "against this component. Your own source for the combined work "
                    "would need to be made available under the same terms."
                )
            if context.use_case == "Embedded":
                return (
                    f"{license.name}: shipping hardware containing this component is "
                    "distribution. Source-disclosure obligations for the combined "
                    "work apply the same way as for traditional software distribution."
                )
            if context.use_case == "SaaS":
                return (
                    f"{license.name} is triggered by distribution, not by network use "
                    "(that is what AGPL is for) -- running it as a server-side SaaS "
                    "backend without distributing any binary generally does not, by "
                    "itself, trigger source disclosure. Flagged for review only "
                    "because some 'SaaS' architectures also distribute a client, "
                    "agent, or on-prem component that would trigger it."
                )
            return f"{license.name} has no restriction triggered by purely internal, non-distributed use."

        if base == "Weak Copyleft":  # LGPL / MPL family
            if not license.applies_to_context(context):
                return f"{license.name}'s distribution-triggered obligations do not apply to internal/non-distributed use."
            if context.modifications_expected:
                return (
                    f"{license.name} requires that modifications to the "
                    "library/covered files themselves be made available under the "
                    "same license if you distribute them, and (for LGPL) that users "
                    "retain the ability to relink against a different version."
                )
            return (
                f"{license.name} allows linking/inclusion from proprietary code, but "
                "requires preserving the ability to swap in a different version of "
                "the component (LGPL) or keeping modified files under the same "
                "license if distributed (MPL). Confirm no undocumented modifications "
                "exist before treating this as fully clear."
            )

        return f"{license.name}: risk category not recognized by this tool -- treat as requiring review."
