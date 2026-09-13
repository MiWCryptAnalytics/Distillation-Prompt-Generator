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
| ANZSRC FoR 2020 | Research (AU/NZ) | yes | 11 disciplines (soil science, geomorphology, polymer/computational/medicinal chemistry, ecotoxicology, systematics, medical physics, actuarial science, tort law, clinical trials); Indigenous studies judged covered via Ethnobiology, Non-Western Philosophy, TCM |
| UNESCO fields of science & technology | Research (int'l) | yes | Confirmed ANZSRC finds; anatomy judged descriptive-grain, food science judged covered (Culinary, Food Eng, Nutrition) |
| PhilPapers / Getty AAT / Grove Music | Field taxonomies (humanities) | yes | Humanities depth pass: 11 disciplines (early modern phil, phenomenology, metaethics, phil of math, scriptural exegesis, paleography, environmental history, composition, animation, painting/printmaking, calligraphy); phil of religion, memory studies, prosody judged covered |
| ABMS/ACGME boards + MeSH top trees | Specialty certification (US) / subject index | yes | Medicine depth pass: 12 disciplines (family medicine, transplant, cardiothoracic, plastics, neurosurgery, pain, addiction, aerospace & hyperbaric, tropical, forensic pathology, paramedicine, genetic counseling); nuclear medicine, hospital medicine, optometry, OT judged folds (MeSH concept-level sweep still pending) |
| AoM divisions + CPA/CFE/GRC bodies | Field taxonomy / professional certification | yes | Business depth pass: 13 disciplines (org theory, change mgmt, DEI, healthcare mgmt, service mgmt, platforms, advertising, consulting, ERM, auditing, forensic accounting, corporate tax, sustainability reporting); compensation & benefits, quality mgmt, brand mgmt, knowledge mgmt judged covered |
| ESCO (13,890 skills) | Skills (EU) | no | Concept-level; candidate for meta-gen QA |
| MSC 2020 / MeSH / PACS-PhySH | Research subject indexes | no | Concept-level depth checks per domain |
| CPC/IPC patent classes | Technology | no | Concept-level for Applied domains |
