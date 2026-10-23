---
name: Trend-source trust
description: Criteria for adding provider adapters to the country-based trend bot.
---

Only label a provider as a search-trend source when it returns actual search-query trend data for the requested region and its metric can be explained. Keep engagement and community popularity in a separate category. Public rankings, unofficial scraping, or APIs that only compare user-supplied keywords are not equivalent to a live list of trending searches. Do not expose those as search trends without a suitable data contract and explicit labeling.

**Why:** The product promises country-based search trends; conflating social popularity or keyword-comparison indices with query trends would mislead users and add fragile dependencies.

**How to apply:** Before adding a provider, verify regional fidelity, authentication requirements, data provenance, and what its returned metric means. Enable credential-dependent providers only after the required credentials are configured.
