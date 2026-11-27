# Issue Proposal: Filter Journal Book Reviews to Prevent Synecdoche Author Mismatches

## Context & Motivation

When checking references for manuscripts citing classic academic monographs or books (e.g., Hannah Arendt's *The Origins of Totalitarianism*, Michel Foucault's *Discipline and Punish*, or Loïc Wacquant's *Punishing the Poor*), CrossRef and Semantic Scholar search queries frequently return journal book reviews as top candidate matches (e.g. `"Book Reviews : The Origins of Totalitarianism. By Hannah Arendt"`).

In the current implementation, `calculate_title_similarity()` awards high scores to these review titles due to title substring and n-gram overlap. Because journal database records for book reviews list the *reviewer* as author (e.g. `G. E. G. Catlin` or `David Garland`), RefChecker selects the review record, triggers a false-positive `Author Mismatch` error, and in `format_corrected_bibtex`, replaces the canonical author with the reviewer's name (the "synecdoche" failure).

## Empirical Benchmark

Tested against a corpus of 27 real-world humanities/social-science references containing 8 monographs:
- **Without filter**: 8 / 27 (29.6%) references falsely matched journal book reviews, resulting in corrupted author corrections.
- **With anti-synecdoche filter**: 0 / 27 (0.0%) false positive matches. Review candidates are automatically rejected, allowing either direct monograph resolution or clean fallback.

## Proposed Solution

1. Introduce an `is_book_review(title: Optional[str]) -> bool` detector in `refchecker.utils.text_utils` identifying common review prefixes:
   `^(?:book\s+reviews?|reviewed\s+work|review(?:\s*article)?|essay\s+review)\s*[:\-—]\s*|^review\s+of\s+`
2. In `find_best_match(search_results, cleaned_title, ...)`:
   - Check if `cleaned_title` itself is a review.
   - If the cited work is NOT a review, skip candidates where `is_book_review(result_title)` is true or `result.get('type') in ('book-review', 'review')`.

## References

- Benchmark script: `scripts/benchmark_synecdoche.py`
- Unit tests: `tests/unit/test_synecdoche_review_filter.py`
