# Cervical Spine — Master Clinical Dossier & Companion Test Atlas

**Live Atlas:** https://azhry-x.github.io/cervical-atlas/  
**Dossier PDF:** [`master_cervical_dossier.pdf`](./master_cervical_dossier.pdf) — 9 pages, A4 portrait, built for Apple Pencil in Notability / GoodNotes.

Sister projects:
- [Knee Complex dossier + atlas](https://github.com/Azhry-X/knee-atlas) — same design system, same page architecture.
- [Ankle & Foot dossier + atlas](https://github.com/Azhry-X/ankle-atlas) — same design system, same page architecture.
- [Lumbar Spine dossier + atlas](https://github.com/Azhry-X/lumbar-atlas) — same design system, same page architecture.
- [Shoulder Complex dossier + atlas](https://github.com/Azhry-X/shoulder-atlas) — same design system, same page architecture.

## What is in the dossier
| Page | Content | Accent |
|---|---|---|
| 1 | Triage, red flags (Canadian C-Spine Rule, NEXUS, serious-pathology CPG quote, cervical artery dysfunction / IFOMPT 2023 framework, Cook 2010 cervical myelopathy 5-item cluster & single tests, Sharp-Purser & upper cervical instability, Quebec Task Force WAD grades 0–IV), pathway router, subjective, body chart | red |
| 2 | CPG 4-classification matrix (mobility deficits, movement coordination impairments / WAD, cervicogenic headaches, radiating pain), Wainner radiculopathy cluster & ULTT A, flexion-rotation test (Ogince, Hall), prognosis (Hush, Walton, Ritchie WhipPredict, Wong, CPG WAD reassurance) | blue |
| 3 | Active cervical ROM write-in table (Rondoni reliability note), CPG exam set, craniocervical flexion test (Jull), deep neck flexor endurance write-in, joint position error (Revel, Treleaven), C5–T1 neurological grid + UMN / myelopathy screen row | blue |
| 4 | Neurodynamic & provocative tests (Rubinstein SR, Wainner single tests, Thoomes Spurling & rule-in / rule-out combinations), Cleland 2007 thoracic manipulation CPR & 2010 trial, Raney cervical traction CPR, PROM dashboard (NDI, PSFS, NPRS, WDQ, TSK-11, CPG outcome quote) | blue |
| 5 | Post-op: surgeon-directed restrictions, ACDF + physiotherapy vs physiotherapy alone (Engquist 2013/2017, Peolsson 2013), structured post-op physiotherapy after ACDF (Wibault 2018), CDA vs ACDF (Wang 2020), dysphagia after ACDF (Xue 2022), post-op re-check, operative log | purple |
| 6 | Electrophysical agents & passive modalities: collar or physiotherapy vs wait-and-see (Kuijper 2009), traction (Graham Cochrane, Fritz 2014, Romeo 2018), low-level laser (Chow 2009), electrotherapy Cochrane (Kroeling 2013), JOSPT CPG & OPTIMa recommendations, parameter log | orange |
| 7 | Manual therapy: JOSPT CPG quotes, manipulation vs mobilisation (Gross 2015), thoracic manipulation (Masaracchio 2019, Cross 2011), C1–C2 self-SNAG (Hall 2007), manipulation + exercise for cervicogenic headache (Jull 2002), dry needling (Chen 2025), vascular safety box (Carnes, Swait & Finch, IFOMPT) & consent box | teal |
| 8 | Exercise & return to activity: Cochrane exercise review (Gross 2015), Jull 2002, MINT acute whiplash (Lamb 2013), PROMISE chronic whiplash (Michaleff 2014), OPTIMa & JOSPT CPG education quotes, CCFT / DNF training progression, 12-week loading log | green |
| 9 | 12-visit flowsheet, discharge milestones (NDI / PSFS / NPRS change vs verified MCIDs by population), discharge summary | slate |

Every statistic carries an evidence marker: **H** high · **M** moderate · **L** low · **E** expert opinion.
Underlined test names open the matching Atlas card; **▸** marks cards with a verified video.

## Repository layout
```
index.html                    Atlas (GitHub Pages entry point) — generated
master_cervical_dossier.html  Dossier (generated, self-contained CSS)
master_cervical_dossier.pdf   Dossier PDF (generated)
src/pages/p1.html … p9.html   Dossier page bodies  ← edit content here
src/dossier.css               Design system
atlas/data/tests.yaml         Atlas cards: steps, criteria, accuracy, evidence, videos, calculators  ← single source of truth
atlas/build_atlas.py          Builds index.html from tests.yaml (page badges/filters = every dossier page that links the card)
atlas/config.py               Atlas base URL
tools/build_dossier.py        Assembles HTML → PDF → runs every check
tools/render_and_check.py     Page count, overflow, overlap, fonts, required safety strings, previews
tools/check_links.py          Verifies every PDF link, Atlas anchor, card source (DOIs via the DOI registry) and video
tools/required_strings.txt    Safety-critical text that must never disappear
fonts/                        Source Sans 3 (OFL)
```

## Rebuild after an edit
One-time setup (Python 3.10+ and Node.js):
```bash
pip install -r requirements.txt
python -m playwright install chromium
npm install
```
Windows, one command (stops at the first failure):
```powershell
powershell -ExecutionPolicy Bypass -File build.ps1            # Atlas + PDF + all checks + link audit
powershell -ExecutionPolicy Bypass -File build.ps1 -SkipLinks # same, without the network link audit
```
Or step by step on any OS:
```bash
python atlas/build_atlas.py                # Atlas
python tools/build_dossier.py              # Dossier PDF + all checks (exit 1 on any problem)
python tools/check_links.py                # links (add --live after the site is published)
```
The dossier build fails on: page count ≠ 9, content overflowing a page / card / cell, overlapping glyphs,
a character missing from Source Sans 3 (font fallback), malformed tables, leaked markup, internal link targets
under 4 mm, or a missing safety string from `tools/required_strings.txt`.
Page previews are written to `preview/` when poppler (`pdftoppm`) or `pip install pypdfium2 pillow` is available.
Authoring shortcuts in `src/pages/*.html` (expanded at build time):
`<a class="test-link" data-atlas="spurling-test">Spurling</a>` · `<a class="info-icon" data-atlas="jospt-2017-neck-pain-cpg"></a>` ·
`<a class="calc-badge" data-atlas="ndi">Calc</a>` · `<a class="guide-badge" href="https://…">JOSPT CPG</a>`.
An unknown `data-atlas` id stops the build.

## Status
Draft cards under clinical review with open-access citations and video demonstrations.
