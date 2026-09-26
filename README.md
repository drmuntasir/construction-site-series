# Construction Site Series

KSCCN anatomical reviews on lasting learning as a scarce permission to **address**, **write**, **select**, **transform**, and **reopen**.

Author: Dr Syed Muntasir Mamun  
ORCID: [0000-0001-6845-2853](https://orcid.org/0000-0001-6845-2853)  
Series dates: 26–27 September 2026

Repository: <https://github.com/drmuntasir/construction-site-series>

## Argument in one paragraph

Lasting learning is not exposure. A fluent pass lights the board and leaves almost nothing. A hard attempt *tags* a place as eligible for a real write. That tag dies unless a scarce resource *captures* it inside a window. Night, spacing, and institutions decide which tagged traces become *gist* and which are forgotten. Later mismatch may *reopen* the gist. Someone always decides which errors count (`θ`), which writes are afforded (`B`), and which stones may not be lifted (the constitutional bit). That someone is the sampling rule. Cognitive sovereignty is owning it — not owning racks.

## Papers

| File | Piece | Grain |
|---|---|---|
| `papers/Mamun_Minds_Construction_Site_Anatomical_Review_VolI.pdf` | Vol-I | Encoding / friction / tags |
| `papers/Mamun_After_the_Hammer_Blows_Anatomical_Review_VolII.pdf` | Vol-II | Consolidation / night |
| `papers/Mamun_Tag_Manifolds_Write_Budgets_Anatomical_Review_VolIII.pdf` | Vol-III | Geometry and substrate |
| `papers/Mamun_Mismatch_Gated_Rewrite_Engineering_Note_I.pdf` | Engineering Note I | Mismatch-gated rewrite interface |
| `papers/Mamun_Who_Owns_the_Sampling_Rule_Anatomical_Review_VolIV.pdf` | Vol-IV | Sovereignty of the sampling rule |
| `papers/Mamun_Construction_Site_Graduate_Teaching_Note.pdf` | Teaching note | Graduate laboratory brief |

Compact model: **P1–P19** plus interface invariants **I1–I5**.

## Laboratory

```bash
python3 lab/construction_site_lab.py
python3 lab/construction_site_lab.py --scenario S4
python3 lab/construction_site_lab.py --list
python3 lab/construction_site_lab.py --seed 7 --verbose
```

Requires Python 3.9+. No third-party packages.

Seed `11` on the unmodified file should report **10/10**. That is preparation. The teaching note treats a predicted FAIL after a perturbation as the actual examination.

| ID | Tests |
|---|---|
| S1 | Fluency factory (P3, P5) |
| S2 | Productive failure then capture (P3, P4, P6) |
| S3 | Archive habit (Note I) |
| S4 | Legal mismatch rewrite (P10, I2, I3, I5) |
| S5 | Idle reopen refused (I2) |
| S6 | Budget theatre (P6, P17, I3) |
| S7 | Constitutional granite (P18) |
| S8 | Named sampling rules (P8, P16) |
| S9 | Workspace / correlation length (P12, P14) |
| S10 | Sovereignty is permission, not location (P15, P18) |

## Regenerating the PDFs

Generators live in `src/` and require ReportLab.

```bash
python3 src/generate_paper.py          # Vol-I
python3 src/generate_paper_vol2.py     # Vol-II
python3 src/generate_paper_vol3.py     # Vol-III
python3 src/generate_paper_engnote1.py # Note I
python3 src/generate_paper_vol4.py     # Vol-IV
python3 src/generate_teaching_note.py  # Teaching note
```

Output paths inside the generators currently write to `/home/workdir/artifacts/` in the original build environment. Edit `OUTPUT` before regenerating locally.

## What the series is not

Not a claim that transformers have sleep spindles. Not a product SDK. Not a statute. Not a quantum-substrate theory (explicitly reserved and left closed).

## Licence

Text and code: [CC BY 4.0](LICENSE).
