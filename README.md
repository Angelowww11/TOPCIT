# TOPCIT Study Lab

An independent, mobile-friendly reviewer built from the supplied TOPCIT study documents.

## What's inside

- 242 unique reviewer items across six areas, with source figures attached to visual questions.
- The source-content check covers all 88 main reviewer pages and all 242 questions. All 164 source picture placements appear on the site.
- The repair list covers 44 questions. It restores missing context, picture choices, page breaks, and 21 clipped figures.
- Source figures show their PDF pages and open at full size when selected. The same figures appear in Practice path, quiz rounds, the question bank, and matching study-guide examples.
- 242 playable items: 44 corrected answers, 168 checked answers, and 30 labeled reviewer-key fallbacks.
- All 91 previously source-only answers have individual findings. All 26 previously unresolved items have a new source review.
- Ambiguous items use the original reviewer key at the learner request. They display **Reviewer answer** and a source caution. They are not labeled as checked answers.
- Practice path contains all 242 questions in fixed source order. It saves the current question, answers, choice order, and study preferences on this device.
- Practice path provides correct-answer-first, optional answer shuffling, explanation and key idea controls, question-number navigation, skipping, reveal, retry, and a separate reset.
- Practice path has unlimited hearts and no timer. It preserves other rounds and XP. All 242 questions accept answers, including the labeled reviewer fallbacks.
- A 67-concept study guide, searchable question bank, 20-question practice, 50-question timed sprint, full review, and missed-question practice.
- Study guide recall prompts and matching source questions. Fifty concepts include a figure cropped from the supplied reviewer PDF; other concepts use source questions without a figure.
- Training Loop with 20 or 30 questions and repeated rounds for missed items, a three-heart Boss Blitz with a shrinking timer, and a six-pair Match Maker across all exam areas.
- Shuffled questions and answer positions, keyboard shortcuts (1–4 and Enter), immediate grading on selection, explanations, streaks, saved items, and local progress.
- Earn XP and study ranks; spend XP on one-use 50/50, shield, and Blitz time boosts. Correct and wrong answers have optional sound and visual feedback. Unfinished quiz and matching rounds can be resumed.
- An installable offline-capable app shell that works on phones, tablets, and computers.
- The Written lab contains all 45 exercises from the separate 17-page reviewer. It retains all 157 substantive Word paragraphs and 28 original pictures.
- Written answers and notes save on this device. Choice exercises provide instant feedback and a correct-answer-first option.
- Written exercises keep checked answers and original responses separate. Exercises 3, 30, and 31 identify gaps in the supplied sources.
- The public `content-audit.html` contains the question-by-question source-content record. `content-audit.json` contains the check data.

The answer marks in `1. TOPCIT Reviewer - Software.pdf` were imported. The review checks all 242 prompts and choice sets. The final pass visually inspects the source pages for the remaining 117 items. It compares duplicate source documents and uses primary references for technical claims. It restores five missing choice sets and nine yellow source highlights. Calculation checks execute the restored Python and SQL examples and test the pairwise table, relational division, subnet arithmetic, and PERT arithmetic.

See the searchable [answer review](answer-review.html) or [review data](answer-review.json) for each item, its source key, study answer, reason, and references. Thirty items have missing information, multiple valid choices, or context-dependent claims. All thirty have a source-marked key, so no guessed answer is needed. `reviewer_fallbacks.py` records the fallback explanations. Their `checkedAnswerIndex` remains null; their playable `answerIndex` follows the reviewer. The original finding stays in `reviewCaveat`. The original import audit remains in `answer-audit.json` as historical data.

Run `python review_answers.py` to apply the review. Run `python check_review.py` to check the repaired keys and calculations. The extraction script, `build_content.py`, applies the review after each source import. Extraction requires the original local PDF and the Python packages `pymupdf` and `Pillow`.

Run `python restore_source_figures.py` to rebuild the 44 repaired examples from their original embedded PDF images. `source-figure-repairs.json` records the source pages, image rectangles, and optional choice labels. The answer review reapplies these figure assignments after every source import.

Run these commands after a source-content change:

```sh
python build_written.py
python audit_content.py
python build_content_report.py
python check_content.py
python check_review.py
```

The written importer needs the original `TOPCIT_Reviewer.pdf` and `TOPCIT_ (2).docx`. The completeness check needs the original main PDF and six Word reviewers. `check_content.py` compares all source paragraphs and picture bytes. It also executes the supplementary SQL and Python examples. The six large textbooks remain learning references; this check does not audit every textbook page.

The theme selector provides Dusk (default), Midnight, Forest, Plum, and Light. The browser saves the selected theme. The responsive design uses a connected study map, softer card shapes, and aligned mobile controls. Motion respects the system setting for reduced motion.

Study notes are concise explanations based on the supplied materials, rather than a page-for-page copy. Figures shown in the guide are source question crops, with PDF page labels. This is a study aid, not an official TOPCIT publication. Progress is stored in the browser on each device; there is no account or server-side tracking.

## Run locally

Serve the folder with any static web server, for example:

```sh
python -m http.server 4399
```

Open `http://localhost:4399`. The site has no build step or runtime dependencies.



