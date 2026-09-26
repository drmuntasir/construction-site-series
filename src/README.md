# PDF generators

The KSCCN volumes were built with ReportLab scripts:

- `generate_paper.py` — Vol-I
- `generate_paper_vol2.py` — Vol-II
- `generate_paper_vol3.py` — Vol-III
- `generate_paper_engnote1.py` — Engineering Note I
- `generate_paper_vol4.py` — Vol-IV
- `generate_teaching_note.py` — graduate teaching note

Place a generator here and edit its `OUTPUT` path before regenerating.

The GitHub file connector used for this repository encodes content as UTF-8 text, so binary PDFs should be added from a local clone:

```bash
git clone https://github.com/drmuntasir/construction-site-series.git
cp /path/to/*.pdf papers/
git add papers/*.pdf
git commit -m "Add KSCCN series PDFs"
git push
```
