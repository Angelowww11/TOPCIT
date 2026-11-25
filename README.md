# TOPCIT Study Lab

An independent, mobile-friendly reviewer built from the supplied TOPCIT study documents.

## What's inside

- 242 unique reviewer items across six areas, with source figures attached to visual questions.
- 212 scored items. The review classifies 44 corrected answers, 168 checked answers, and 30 defective or ambiguous items.
- All 91 previously source-only answers have individual findings. All 26 previously unresolved items have a new source review.
- Defective items remain visible for study and do not enter scored rounds. Original source keys remain separate from study answers.
- Practice path contains all 242 questions in fixed source order. It saves the current question, answers, choice order, and study preferences on this device.
- Practice path provides correct-answer-first, optional answer shuffling, explanation and key idea controls, question-number navigation, skipping, reveal, retry, and a separate reset.
- Practice path has unlimited hearts and no timer. It preserves other rounds and XP. Defective questions remain study-only and cannot receive a correct or wrong mark.
- A 67-concept study guide, searchable question bank, 20-question practice, 50-question timed sprint, full review, and missed-question practice.
- Study guide recall prompts and matching source questions. Fifty concepts include a figure cropped from the supplied reviewer PDF; other concepts use source questions without a figure.
- Training Loop with 20 or 30 questions and repeated rounds for missed items, a three-heart Boss Blitz with a shrinking timer, and a six-pair Match Maker across all exam areas.
- Shuffled questions and answer positions, keyboard shortcuts (1–4 and Enter), immediate grading on selection, explanations, streaks, saved items, and local progress.
- Earn XP and study ranks; spend XP on one-use 50/50, shield, and Blitz time boosts. Correct and wrong answers have optional sound and visual feedback. Unfinished quiz and matching rounds can be resumed.
- An installable offline-capable app shell that works on phones, tablets, and computers.

The answer marks in `1. TOPCIT Reviewer - Software.pdf` were imported. The review checks all 242 prompts and choice sets. The final pass visually inspects the source pages for the remaining 117 items. It compares duplicate source documents and uses primary references for technical claims. It restores five missing choice sets and nine yellow source highlights. Calculation checks execute the restored Python and SQL examples and test the pairwise table, relational division, subnet arithmetic, and PERT arithmetic.

See the searchable [answer review](answer-review.html) or [review data](answer-review.json) for each item, its source key, study answer, reason, and references. Thirty items have missing information, multiple valid choices, or context-dependent claims. They remain study-only. The original import audit remains in `answer-audit.json` as historical data.

Run `python review_answers.py` to apply the review. Run `python check_review.py` to check the repaired keys and calculations. The extraction script, `build_content.py`, applies the review after each source import. Extraction requires the original local PDF and the Python packages `pymupdf` and `Pillow`.

The theme selector provides Dusk (default), Midnight, Forest, Plum, and Light. The browser saves the selected theme. The responsive design uses a connected study map, softer card shapes, and aligned mobile controls. Motion respects the system setting for reduced motion.

Study notes are concise explanations based on the supplied materials, rather than a page-for-page copy. Figures shown in the guide are source question crops, with PDF page labels. This is a study aid, not an official TOPCIT publication. Progress is stored in the browser on each device; there is no account or server-side tracking.

## Run locally

Serve the folder with any static web server, for example:

```sh
python -m http.server 4399
```

Open `http://localhost:4399`. The site has no build step or runtime dependencies.



