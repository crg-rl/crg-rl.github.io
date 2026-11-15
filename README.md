# Beyond Forgetting · Continual Reasoning Gym

Source for <https://crg-rl.github.io/>. The page links the paper, released CRG code and presentation. Scientific page content is unchanged by the slide refresh.

## Presentation

The 17-slide, 15–16-minute talk follows: **Background → Environments → Diagnosis & method → Results & analysis → Takeaways**.

- [PDF](assets/slides/continual-reasoning-gym-slides.pdf)
- [Editable PPTX](assets/slides/continual-reasoning-gym-slides.pptx)
- [Outline](slides/outline.md) and [Chinese speaker notes](slides/speaker-notes.md)

The talk distinguishes CRG (the environment) from CPR (the method). It uses the original environment, task, method and jugs case figures. Native slide text, shape-based diagrams and result charts are editable in PowerPoint. Paper figures are high-resolution images in PPTX; the PDF preserves their original vectors where available. The two Background pages use purpose-built explanatory illustrations of arriving tasks and cross-task learning relationships; these illustrations are embedded images, while their titles and short questions remain editable.

## Rebuild and verify

Python 3 with `python-pptx`, `PyMuPDF`, `reportlab` and `Pillow`; the exporter uses macOS Arial and Menlo fonts. No PowerPoint/Keynote automation or external server is needed.

```sh
python3 scripts/build_slides.py
python3 scripts/render_slides_pdf.py assets/slides/continual-reasoning-gym-slides.pptx assets/slides/continual-reasoning-gym-slides.pdf
python3 scripts/freeze_slides_release.py
python3 scripts/validate_artifacts.py
python3 scripts/test_build.py
python3 scripts/render_slide_previews.py --out /tmp/crg-slide-previews
```

`slides/figure-assets.json` binds original figures and crops; `slides/sources/` preserves the result tables and paper identities. `slides/release-manifest.json` binds the released pair to its source. The linked public paper and the newer author figure renderings are recorded separately in source metadata; there is no version taxonomy on audience-facing slides.

For a private browser preview, open `index.html` directly or bind a local server **only to 127.0.0.1**. Publication uses this repository’s existing GitHub Pages deployment.
