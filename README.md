# TOPCIT Study Lab

An independent, mobile-friendly reviewer built from the supplied TOPCIT study documents.

## What's inside

- 242 unique reviewer items across six areas, including 141 cropped source illustrations.
- 223 scored items. Questions with missing or contradictory answer keys remain visible for study, but are not used in scored rounds.
- A 50-concept study guide, searchable question bank, 20-question practice, 50-question timed sprint, full review, and missed-question practice.
- Shuffled questions and answer positions, keyboard shortcuts (1–4 and Enter), immediate explanations, streaks, saved items, local progress, and an installable offline-capable app shell.

The answer marks in `1. TOPCIT Reviewer - Software.pdf` were imported, then visually checked where they conflicted with the wording or figures. See [answer-audit.json](answer-audit.json) for corrections and study-only ambiguities. The extraction script is [build_content.py](build_content.py); it requires the original local PDF and Python packages `pymupdf` and `Pillow`.

Study notes are concise explanations based on the supplied materials. This is a study aid, not an official TOPCIT publication. Progress is stored in the browser on each device; there is no account or server-side tracking.

## Run locally

Serve the folder with any static web server, for example:

```sh
python -m http.server 4399
```

Open `http://localhost:4399`. The site has no build step or runtime dependencies.

