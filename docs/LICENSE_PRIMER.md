# Open Source License Primer

Plain-English summary of the licenses this tool recognizes, and why context
changes their risk. This is educational background, not legal advice --
see [DISCLAIMER.md](../DISCLAIMER.md).

## Permissive: MIT, Apache-2.0, BSD-2/3-Clause, ISC, Unlicense

No source disclosure requirement, no restriction on commercial use or
modification. The only real obligation is retaining the copyright notice
(and, for Apache-2.0, noting significant changes and being aware of its
patent-retaliation clause). Risk level: 🟢 Safe in every context this tool
models.

## Weak copyleft: LGPL-2.1, LGPL-3.0, MPL-2.0

Lets you combine the library with proprietary code, but with conditions:

- **LGPL** requires that modifications *to the library itself* be shared if
  you distribute them, and that the end user retain the ability to relink
  against a different version of the library (e.g. via dynamic linking).
  It does not require disclosing the source of the application that merely
  *uses* the library.
- **MPL-2.0** is file-level copyleft: modified MPL-licensed files must stay
  under MPL-2.0 if distributed, but you can freely combine them with
  proprietary code kept in separate files.

Risk level: 🟢 Safe for internal/non-distributed use; 🟡 Needs Review or
🔴 Action Required once you distribute, depending on whether you've
modified the covered files.

## Strong copyleft: GPL-2.0, GPL-3.0

The obligation that most people mean by "copyleft": if you **distribute** a
binary that includes or links against GPL code, you must provide the
corresponding source code for the combined work under the same license.

**This is a distribution trigger, not a network-use trigger.** Running GPL
code as the backend of a hosted service, without distributing any binary
to your customers, generally does not by itself require you to disclose
your source -- this is the long-standing "ASP/SaaS loophole" that AGPL (see
below) exists specifically to close.

- Internal, non-distributed use: 🟢 Safe.
- SaaS: 🟡 Needs Review -- flagged because some products marketed as
  "SaaS" also ship a client, on-prem agent, or appliance that *would* count
  as distribution; verify what actually gets distributed.
- Distributed or Embedded (shipping hardware containing the code counts as
  distribution): 🔴 Action Required.

GPL-3.0 adds an explicit patent grant with a litigation-retaliation clause
and an anti-tivoization provision (users must be able to install modified
versions on hardware that ships with the software, where applicable) on
top of GPL-2.0's terms.

## Network copyleft: AGPL-3.0

Closes the SaaS loophole described above: if you run a **modified** version
of AGPL-licensed software and users interact with it **over a network**,
you must offer them the corresponding source -- even if you never
distribute a binary. This is AGPL-3.0 Section 13.

Important nuance this tool is deliberately conservative about: "network
use" doesn't require the users to be external customers. An internal web
application used only by employees still involves users interacting with
the software over a network. This tool does not automatically clear AGPL
as 🟢 Safe for `use_case="Internal"` -- it returns 🟡 Needs Review instead,
because the business-context questionnaire doesn't currently distinguish
"internal, no network exposure at all" from "internal, but served over an
intranet." Confirm actual exposure before treating an AGPL dependency as
low risk.

## Unknown license

If a dependency's license can't be resolved (not in the SBOM's declared
licenses, not in this tool's offline dataset), it is always 🔴 Action
Required. An unresolved license is not evidence of "probably fine" -- it
means neither the permissions nor the obligations are confirmed.

## Terminology note

This tool avoids folk terms like "GPL contamination" or "viral license" in
favor of describing what a license actually requires (e.g. "source
disclosure requirement triggered by distribution"). Accurate language is
also more defensible if a finding is ever challenged.
