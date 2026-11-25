# TOPCIT Study Lab

An independent, mobile-friendly reviewer built from the supplied TOPCIT study documents.

## What's inside

- 242 unique reviewer items across six areas, including 141 cropped source illustrations.
- 216 scored items. The review classifies 30 corrected answers, 95 checked answers, 91 source-only answers, and 26 unresolved items.
- Unresolved items remain visible for study and do not enter scored rounds. Source-only answers retain the reviewer key and display an explicit verification notice.
- A 67-concept study guide, searchable question bank, 20-question practice, 50-question timed sprint, full review, and missed-question practice.
- Study guide recall prompts and matching source questions. Fifty concepts include a figure cropped from the supplied reviewer PDF; other concepts use source questions without a figure.
- Training Loop with 20 or 30 questions and repeated rounds for missed items, a three-heart Boss Blitz with a shrinking timer, and a six-pair Match Maker across all exam areas.
- Shuffled questions and answer positions, keyboard shortcuts (1–4 and Enter), immediate explanations, streaks, saved items, and local progress.
- Earn XP and study ranks; spend XP on one-use 50/50, shield, and Blitz time boosts. Correct and wrong answers have optional sound and visual feedback. Unfinished quiz and matching rounds can be resumed.
- An installable offline-capable app shell that works on phones, tablets, and computers.

The answer marks in `1. TOPCIT Reviewer - Software.pdf` were imported. The second review screens all 242 prompts and choice sets. It visually checks the suspect figures and restores nine yellow source highlights that the red-text importer missed. Source-only labels identify items that still need independent verification. See the searchable [answer review](answer-review.html) or [review data](answer-review.json) for each item, its source key, its study answer, and the review reason. The original import audit remains in `answer-audit.json` as historical data.

Run `python review_answers.py` to apply the second review. The extraction script, `build_content.py`, runs it after each source import. The extraction requires the original local PDF and the Python packages `pymupdf` and `Pillow`.

The theme selector provides Dusk (default), Midnight, Forest, Plum, and Light. The browser saves the selected theme. The darker surface hierarchy takes visual reference from Linear and Raycast while retaining the reviewer layout.

Study notes are concise explanations based on the supplied materials, rather than a page-for-page copy. Figures shown in the guide are source question crops, with PDF page labels. This is a study aid, not an official TOPCIT publication. Progress is stored in the browser on each device; there is no account or server-side tracking.

## Run locally

Serve the folder with any static web server, for example:

```sh
python -m http.server 4399
```

Open `http://localhost:4399`. The site has no build step or runtime dependencies.



