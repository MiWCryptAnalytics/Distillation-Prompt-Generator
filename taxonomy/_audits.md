# Coverage audit registry

Which external catalogs the taxonomy has been swept against, and what each
found. Future rounds: pick an unswept catalog, sweep, record here. (Root-level
file; the engine only loads `<domain>/<discipline>.json`.)

| Catalog | Type | Swept | Outcome |
|---|---|---|---|
| Dewey Decimal (DDC) | Library | yes | Framed the original 6 domains + per-domain tables |
| Library of Congress (LCC) | Library | yes | Same; every discipline carries an LCC anchor |
| OECD Frascati fields | Research | yes | Framed science/engineering/medical domains |
| ACM CCS | Research (computing) | yes | Computing disciplines in Applied |
| JEL codes | Research (economics) | yes | Economics & Money table |
| BLS SOC 2018 (867 occupations) | Occupational (US) | yes | 14 disciplines (forestry, fisheries, architecture practice, health informatics, seamanship, mortuary science, ...) |
| O*NET 33 knowledge areas | Occupational (US) | yes | 33/33 covered after adding Graphic Design & Typography |
| ISCO-08 (ILO) | Occupational (int'l) | yes | Traditional & Complementary Medicine; Midwifery |
| ISCED-F 2013 / CIP | Educational programs | yes | All 10 broad fields covered; no new finds |
| NAICS/ISIC | Industry | yes | Covered; casino/gaming ops noted as marginal |
| US state licensing boards | Regulatory | yes | Confirmed midwifery, TCM; massage therapy gap-listed |
| ESCO (13,890 skills) | Skills (EU) | no | Concept-level; candidate for meta-gen QA |
| MSC 2020 / MeSH / PACS-PhySH | Research subject indexes | no | Concept-level depth checks per domain |
| CPC/IPC patent classes | Technology | no | Concept-level for Applied domains |
