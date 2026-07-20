# Regulatory Context

Why an open source inventory isn't just a legal question anymore -- four EU
digital regulations now touch supply-chain/component visibility directly.
Verified against EUR-Lex and legislative tracking sources as of July 2026.
Always check the primary source before relying on a specific figure.

## 1. Cyber Resilience Act (CRA) -- Regulation (EU) 2024/2847

- **Source:** https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng
- Published in the Official Journal: 20 November 2024. In force: 10 December 2024.
- **Staggered applicability** -- the most commonly misstated fact about the CRA:
  - Vulnerability/incident reporting obligations (Art. 14): from **11 September 2026**
  - Essential requirements, conformity assessment, CE marking: from **11 December 2027**
- Relevance to open source: a "product with digital elements" must be
  security-by-design and have its components documented. Open source
  dependencies are components like any other -- they need to be tracked
  (e.g. via SBOM) and their known vulnerabilities managed, regardless of
  whether the code itself was written in-house.
- Penalties: up to €15M/2.5% (essential requirements), €10M/2% (other
  obligations), €5M/1% (misleading information to authorities).

## 2. NIS2 Directive -- Directive (EU) 2022/2555

- **Source:** https://eur-lex.europa.eu/eli/dir/2022/2555/oj
- A **directive**, not a regulation: binding only via each Member State's
  national transposition law. Transposition deadline: 17 October 2024.
- Relevance to open source: NIS2's supply-chain-security obligation
  requires Essential/Important Entities to assess risk from third-party
  components -- open source is a third-party component, and an inventory
  of what's in use is a prerequisite for that assessment.
- Penalties (Member-State minimum ceilings, some go higher): Essential
  Entities ≥ €10M/2%; Important Entities ≥ €7M/1.4%.

## 3. EU Data Act -- Regulation (EU) 2023/2854

- **Source:** https://eur-lex.europa.eu/eli/reg/2023/2854/oj
- In force: 11 January 2024.
- **Two separate deadlines** -- do not conflate them:
  - General applicability (data access, portability, third-party sharing,
    cloud switching): **12 September 2025**
  - Connected-product "access by design" obligation for newly placed
    products: **12 September 2026**
- Relevance to open source: some open source components (e.g. embedded
  data-collection agents, telemetry libraries) may themselves impose
  restrictions on how collected data can be used or shared -- worth
  checking alongside your own Data Act obligations, particularly for
  industrial/machine data.
- No EU-wide penalty cap (unlike GDPR) -- Member States set their own,
  with a Commission-recommended floor of ~€10M/2% for most violations,
  ~€1M/0.1% for B2G data-sharing violations.

## 4. EU AI Act -- Regulation (EU) 2024/1689

- **Source:** https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- In force: 1 August 2024.
- Phase-in: prohibited practices + AI literacy (2 Feb 2025); GPAI model
  obligations + governance (2 Aug 2025); high-risk systems -- **originally**
  2 Aug 2026 (standalone, Annex III) / 2 Aug 2027 (embedded safety
  components, Annex I).
- **Time-sensitive:** a Digital Omnibus political agreement (6-13 May 2026)
  defers both high-risk deadlines: Annex III standalone systems to
  **2 December 2027**, Annex I embedded safety components to
  **2 August 2028**. Formal adoption/OJ publication was still pending as of
  this writing -- reconfirm before relying on either date.
- Relevance to open source: many high-risk AI systems are built on open
  source ML frameworks and pretrained models. If your product includes
  AI/ML and any of it is open source, the documentation, logging, and
  human-oversight obligations for high-risk systems apply to the system as
  a whole -- using an open source model doesn't reduce that obligation.
- Penalties: up to €35M/7% (prohibited practices), €15M/3% (high-risk and
  most other obligations), €7.5M/1% (misleading information). Not a flat
  6% -- a figure that circulates informally but doesn't match any tier in
  Article 99.

## Common citation errors this tool corrects

- Citing the CRA as "EU 2024/2599" (not a real citation; correct is
  2024/2847) or describing it as fully enforced since September 2024
  without the staggered dates.
- Citing the EU Data Act as "EU 2024/2897" (correct is 2023/2854) or
  treating September 2026 as its only/main deadline (general applicability
  was September 2025; September 2026 is the narrower design obligation).
- Citing AI Act penalties as a flat "6% of global revenue" instead of the
  actual tiered structure (7% / 3% / 1%).
