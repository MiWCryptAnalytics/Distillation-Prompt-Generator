# Medicine & Health Sciences — coverage map

Breadth pass across clinical medicine, its diagnostic and foundational sciences,
and population health, mapped to established classification systems. (Starts with
`_` / not `.json`, so the engine ignores it.)

Reference systems used:
- **DDC** — Dewey Decimal: 610 medicine, 611-612 anatomy/physiology,
  613 preventive, 614 public health, 615 pharmacology, 616 internal medicine,
  617 surgery, 618 gynecology/pediatrics
- **LCC** — Library of Congress, R schedule: R medicine (general), RA public
  health, RB pathology, RC internal medicine, RD surgery, RG gynecology,
  RJ pediatrics, RM therapeutics
- **OECD** — Frascati "Medical & Health Sciences": basic medicine,
  clinical medicine, health sciences, medical biotechnology

| Discipline | Branch | DDC | LCC |
|---|---|---|---|
| Cardiology | Internal medicine | 616.12 | RC681+ |
| Oncology | Internal medicine | 616.994 | RC254+ |
| Neurology | Internal medicine | 616.8 | RC346+ |
| Infectious Disease | Internal medicine | 616.9 | RC109+ |
| Clinical Immunology & Allergy | Internal medicine | 616.97 | RC583+ |
| Endocrinology & Metabolism | Internal medicine | 616.4 | RC648+ |
| Pulmonology | Internal medicine | 616.2 | RC705+ |
| Nephrology | Internal medicine | 616.61 | RC902+ |
| Gastroenterology | Internal medicine | 616.33 | RC799+ |
| Hematology | Internal medicine | 616.15 | RC633+ |
| Psychiatry & Mental Health | Clinical | 616.89 | RC435+ |
| Rehabilitation & Physical Medicine | Clinical | 617.03 | RM695+ |
| Anesthesiology & Critical Care | Perioperative & acute | 617.96 | RD78.3+ |
| Surgery & Perioperative Medicine | Perioperative & acute | 617 | RD |
| Emergency & Trauma Medicine | Perioperative & acute | 616.025 | RC86+ |
| Radiology & Medical Imaging | Diagnostics | 616.0757 | RC78+ |
| Pathology & Laboratory Medicine | Diagnostics | 616.07 | RB |
| Obstetrics & Gynecology | Reproductive & life-stage | 618 | RG |
| Pediatrics & Neonatology | Reproductive & life-stage | 618.92 | RJ |
| Pharmacology & Therapeutics | Foundational | 615.1 | RM300+ |
| Toxicology | Foundational | 615.9 | RA1190+ |
| Medical Genetics & Genomic Medicine | Foundational | 616.042 | RB155 |
| Nutrition & Dietetics | Population & preventive | 613.2 | RM214+ |
| Public Health & Preventive Medicine | Population & preventive | 614 | RA |
| Dermatology | Internal medicine | 616.5 | RL |
| Ophthalmology & Vision Science | Sensory & surgical | 617.7 | RE |
| Otolaryngology | Sensory & surgical | 617.51 | RF |
| Urology | Sensory & surgical | 616.6 | RC870+ |
| Orthopedics & Musculoskeletal Medicine | Sensory & surgical | 616.7 | RD701+ |
| Geriatrics | Life-stage | 618.97 | RC952+ |
| Palliative & End-of-Life Care | Life-stage | 616.029 | R726.8 |
| Sports Medicine | Clinical | 617.1027 | RC1210 |
| Veterinary Medicine | Allied & professional | 636.089 | SF600+ |
| Nursing Science | Allied & professional | 610.73 | RT |
| Dentistry & Oral Health | Allied & professional | 617.6 | RK |
| Pharmacy Practice | Allied & professional | 615.4 | RS |
| Speech-Language Pathology & Audiology | Allied & professional | 616.855 | RC423 |
| Health Informatics | Allied & professional | 610.285 | R858 |
| Occupational & Environmental Medicine | Population & preventive | 616.9803 | RC963 |
| Traditional & Complementary Medicine | Allied & professional | 615.5 | R733 |
| Midwifery & Perinatal Practice | Reproductive & life-stage | 618.2 | RG950 |
| Rheumatology | Internal medicine | 616.723 | RC927 |
| Sleep Medicine | Clinical | 616.8498 | RC547 |
| Chiropractic, Massage & Manual Therapies | Allied & professional | 615.534 | RZ241/RM721 |
| Clinical Trial Design & Biostatistics | Foundational | 610.724 | R853.C55 |
| Pastoral Care & Chaplaincy | Allied & professional | 259.4 | BV4335 |
| Family Medicine & Primary Care | Clinical | 610 | R729.5.G4 |
| Transplant Medicine & Surgery | Perioperative & acute | 617.95 | RD120.7 |
| Cardiothoracic Surgery & Perfusion | Perioperative & acute | 617.412 | RD598 |
| Plastic & Reconstructive Surgery | Perioperative & acute | 617.952 | RD118 |
| Neurosurgery | Perioperative & acute | 617.48 | RD593 |
| Pain Medicine | Clinical | 616.0472 | RB127 |
| Addiction Medicine | Clinical | 616.86 | RC564 |
| Aerospace & Hyperbaric Medicine | Population & preventive | 616.98021 | RC1062/RC1005 |
| Tropical & Travel Medicine | Internal medicine | 616.9883 | RC961 |
| Forensic Pathology & Legal Medicine | Diagnostics | 614.1 | RA1063 |
| Paramedicine & Prehospital Care | Perioperative & acute | 362.188 | RC86.7 |
| Genetic Counseling | Foundational | 616.042 | RB155.7 |

## Boundary notes & known gaps
- **Biomedical *engineering*** (devices, imaging hardware, prosthetics) lives in
  Applied Sciences & Tech; this domain is the clinical/physiological treatment.
- **Epidemiology** has a disease-dynamics treatment in Life Sciences; Public
  Health here covers screening, prevention, and health systems.
- _The audit round filled: dermatology, ophthalmology, otolaryngology, urology,
  orthopedics, geriatrics, palliative care, sports medicine, plus veterinary
  medicine, nursing science, and dentistry._
- _The SOC audit filled: pharmacy practice, speech-language pathology &
  audiology, occupational & environmental medicine, plus health informatics._
- _The catalog audit (ISCO-08, licensing boards) added Traditional &
  Complementary Medicine and Midwifery & Perinatal Practice._
- _The gap-fill round added Rheumatology and Sleep Medicine — both board
  specialties no catalog sweep had flagged (a caveat on declaring saturation
  from external catalogs alone) — plus Chiropractic, Massage & Manual
  Therapies, closing the licensing-board gap; per the ethics note it is framed
  descriptively and critically (evidence debates, risk screening)._
- _The second gap-fill pass added Pastoral Care & Chaplaincy (board-certified
  chaplaincy, framed evidentially per the ethics note); the ANZSRC/UNESCO
  sweep added Clinical Trial Design & Biostatistics (trial methodology,
  distinct from meta-science's publication-system concepts and Life Sciences'
  disease-dynamics epidemiology)._
- _The medicine depth pass (ABMS/ACGME specialty boards + MeSH top trees)
  added 12 disciplines. Generalist and process: Family Medicine & Primary Care
  (undifferentiated-presentation reasoning no organ specialty holds),
  Paramedicine & Prehospital Care (field decisions; hospital-side stays in
  Emergency & Trauma), Genetic Counseling (communication and duty questions;
  variant science stays in Medical Genetics). Surgical: Transplant,
  Cardiothoracic & Perfusion, Plastic & Reconstructive, Neurosurgery (each
  carved around Surgery & Perioperative's general concepts). Cross-cutting:
  Pain Medicine (modality mechanisms; chronification stays in Rehabilitation),
  Addiction Medicine (treatment practice; reward circuitry stays in
  Psychiatry — its former fold note is hereby closed), Aerospace & Hyperbaric
  Medicine, Tropical & Travel Medicine, Forensic Pathology & Legal Medicine
  (autopsy interpretation; criminalistics stays in Applied)._
- _The final gap-fill round added the remaining 8 open disciplines: Optometry,
  Physician Assistant Studies, Hospital Medicine, Nuclear Medicine &
  Radiopharmaceutical Therapy, Wilderness & Expedition Medicine, Podiatric
  Medicine, Vaccinology, and Occupational Therapy._
- No open discipline gaps currently listed.
- Gross anatomy stays distributed across Physiology, Surgery, and Radiology:
  its grain is descriptive rather than mechanistic, a poor fit for the 12
  adversarial trajectories.
