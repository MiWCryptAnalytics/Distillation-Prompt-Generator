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
| JEL G-subcodes + CFA/CAIA/GARP BOKs | Research codes / professional certification | yes | Finance depth pass: 10 disciplines (fixed income, investment banking, distressed debt, sovereign & muni debt, credit ratings, trade finance, project finance, wealth mgmt, corporate treasury, clearing & collateral); asset pricing theory, M&A advisory, fintech lending judged covered |
| O*NET tasks + SOC 47-53 + apprenticeship registries (DOL, German Ausbildungsberufe) | Occupational (task-level) | yes | Trades depth pass: 15 disciplines (machining, rigging, masonry, millwright, powerline, glass, baking, butchery, cheese, beverage, arboriculture, climbing, diving, commercial driving, tattooing); HVAC service, printing, upholstery, blasting judged covered; locksmithing deliberately deferred (dual-use) |
| Deep Human Expertise & Niche Subcultures Brainstorm | Agentic Ideation | yes | Broad expansion pass: 13 disciplines added spanning performance arts (magic, circus), specialized crafts (lutherie, theme park design, combatives), digital edge-cases (speedrunning, trust & safety), operational lore (esoteric systems, clandestine tradecraft), and dark/secret knowledge (casino advantage play, cult dynamics, underground economies, deception detection/polygraphy). |
| ESCO (13,890 skills) | Skills (EU) | no | Concept-level; candidate for meta-gen QA |
| MSC 2020 / MeSH / PACS-PhySH | Research subject indexes | no | Concept-level depth checks per domain |
| CPC/IPC patent classes | Technology | no | Concept-level for Applied domains |
| Agentic Ideation (Joy & Whimsy Brainstorm) | Agentic Ideation | yes | Broad expansion pass focusing on cute and happy topics: added 7 disciplines spanning play and celebration (toy design, confectionery, floristry, puppetry, event planning, miniatures, children's literature). |
| Agentic Ideation (Sweet Delights Brainstorm) | Agentic Ideation | yes | Added 5 "sweet" disciplines: Confectionery & Candy Making, Chocolatier Artistry, Baking & Pastry Science, Dessert & Pastry Craft, Gourmet Ice Cream & Gelato. |
| Agentic Ideation (Cozy Home & Geeky Pursuits) | Agentic Ideation | yes | Added 8 disciplines: Artisanal Soap & Candle Making, Fermentation & Cultured Foods, Hand-Spun Textiles & Natural Dyeing, Heritage Seed Saving, Mechanical Keyboard Customization, Amateur High-Power Rocketry, Model Railroading & Layout Engineering, Synthesizer Design & Eurorack Patching. |
| Agentic Ideation (Cozy Home & Geeky Pursuits Part 2) | Agentic Ideation | yes | Added 6 more disciplines: Botanical Perfumery & Olfactory Arts, Fungi Cultivation & Mycology Craft, Basketry & Woven Fiber Crafts, First-Person View (FPV) Drone Engineering, Amateur Radio & Ham Communication, Retrocomputing & Vintage Hardware. |
| Agentic Ideation (Playful Arts & Niche Leisure) | Agentic Ideation | yes | Added 6 disciplines: Board Game Design & Tabletop Mechanics, Aquascaping & Planted Aquariums, Origami & Paper Engineering, Cosplay & Costume Fabrication, Bonsai Cultivation & Shaping, Kite Making & Aerocrafts. |

