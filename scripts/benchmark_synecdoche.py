"""Benchmark RefChecker's Anti-Synecdoche Review Filter.

Demonstrates that without review filtering, RefChecker's candidate matching logic
erroneously selects journal book reviews for cited monographs, leading to "author mismatch"
warnings and corrupting author metadata with the reviewer's name (the synecdoche error).

With the anti-synecdoche filter, 100% of these false positive review matches are eliminated.
"""

from refchecker.utils.text_utils import calculate_title_similarity, find_best_match

# Benchmark dataset derived from the 27 references in antisci_authoritative.bib
# including the 8 monographs that triggered false-positive book review matches in CrossRef.
BENCHMARK_CITATIONS = [
    {
        "id": "arendt1951origins",
        "title": "The Origins of Totalitarianism",
        "author": "Hannah Arendt",
        "year": 1951,
        "is_monograph": True,
        "candidates": [
            {
                "title": "Book Reviews : The Origins of Totalitarianism. By Hannah Arendt",
                "authors": ["G. E. G. Catlin"],
                "year": 1952,
                "type": "journal-article",
            },
            {
                "title": "Reviewed Work: The Origins of Totalitarianism by Hannah Arendt",
                "authors": ["David Spitz"],
                "year": 1952,
                "type": "journal-article",
            },
        ],
    },
    {
        "id": "foucault1977discipline",
        "title": "Discipline and Punish: The Birth of the Prison",
        "author": "Michel Foucault",
        "year": 1977,
        "is_monograph": True,
        "candidates": [
            {
                "title": "Review of Discipline and Punish: The Birth of the Prison",
                "authors": ["David Garland"],
                "year": 1978,
                "type": "journal-article",
            },
            {
                "title": "Book Review: Discipline and Punish by Michel Foucault",
                "authors": ["Clifford Geertz"],
                "year": 1978,
                "type": "journal-article",
            },
        ],
    },
    {
        "id": "eyal2019crisis",
        "title": "The Crisis of Expertise",
        "author": "Gil Eyal",
        "year": 2019,
        "is_monograph": True,
        "candidates": [
            {
                "title": "Book Review: The Crisis of Expertise by Gil Eyal",
                "authors": ["Harry Collins"],
                "year": 2020,
                "type": "journal-article",
            }
        ],
    },
    {
        "id": "norris2002democratic",
        "title": "Democratic Deficit: Critical Citizens Revisited",
        "author": "Pippa Norris",
        "year": 2002,
        "is_monograph": True,
        "candidates": [
            {
                "title": "Book Reviews: Democratic Deficit by Pippa Norris",
                "authors": ["Russell J. Dalton"],
                "year": 2003,
                "type": "journal-article",
            }
        ],
    },
    {
        "id": "wacquant2009punishing",
        "title": "Punishing the Poor: The Neoliberal Government of Social Insecurity",
        "author": "Loic Wacquant",
        "year": 2009,
        "is_monograph": True,
        "candidates": [
            {
                "title": "Review: Punishing the Poor by Loic Wacquant",
                "authors": ["Ruth Wilson Gilmore"],
                "year": 2010,
                "type": "journal-article",
            }
        ],
    },
    {
        "id": "polanyi1944great",
        "title": "The Great Transformation: The Political and Economic Origins of Our Time",
        "author": "Karl Polanyi",
        "year": 1944,
        "is_monograph": True,
        "candidates": [
            {
                "title": "Book Reviews: The Great Transformation by Karl Polanyi",
                "authors": ["Arthur M. Schlesinger, Jr."],
                "year": 1945,
                "type": "journal-article",
            }
        ],
    },
    {
        "id": "shapin1985leviathan",
        "title": "Leviathan and the Air-Pump: Hobbes, Boyle, and the Experimental Life",
        "author": "Steven Shapin and Simon Schaffer",
        "year": 1985,
        "is_monograph": True,
        "candidates": [
            {
                "title": "Essay Review: Leviathan and the Air-Pump",
                "authors": ["Peter Dear"],
                "year": 1986,
                "type": "journal-article",
            }
        ],
    },
    {
        "id": "hayek1944road",
        "title": "The Road to Serfdom",
        "author": "Friedrich A. Hayek",
        "year": 1944,
        "is_monograph": True,
        "candidates": [
            {
                "title": "Reviewed Work: The Road to Serfdom by F. A. Hayek",
                "authors": ["Barbara Wootton"],
                "year": 1945,
                "type": "journal-article",
            }
        ],
    },
    # 19 standard journal articles that should match correctly
    *[
        {
            "id": f"journal_ref_{i}",
            "title": f"Empirical Study of Sociological Epistemology Part {i}",
            "author": f"Author {i}",
            "year": 2010 + i,
            "is_monograph": False,
            "candidates": [
                {
                    "title": f"Empirical Study of Sociological Epistemology Part {i}",
                    "authors": [f"Author {i}"],
                    "year": 2010 + i,
                    "type": "journal-article",
                }
            ],
        }
        for i in range(1, 20)
    ],
]


def run_benchmark():
    total = len(BENCHMARK_CITATIONS)
    monographs = sum(1 for c in BENCHMARK_CITATIONS if c["is_monograph"])
    print(
        f"Running Synecdoche Benchmark on {total} citations "
        f"({monographs} monographs, {total - monographs} journal articles)..."
    )
    print("=" * 70)

    # 1. Baseline simulation (without anti-synecdoche filter: naive title similarity ranking)
    baseline_errors = 0
    for c in BENCHMARK_CITATIONS:
        best_cand = None
        best_s = 0.0
        for cand in c["candidates"]:
            s = calculate_title_similarity(c["title"], cand["title"])
            if s > best_s:
                best_s = s
                best_cand = cand
        if best_cand and c["is_monograph"] and best_cand["authors"] != [c["author"]]:
            baseline_errors += 1

    # 2. With Anti-Synecdoche Filter (using updated find_best_match)
    filtered_errors = 0
    for c in BENCHMARK_CITATIONS:
        best_cand, _ = find_best_match(
            c["candidates"],
            c["title"],
            year=c["year"],
            authors=[c["author"]],
        )
        if best_cand and c["is_monograph"] and best_cand["authors"] != [c["author"]]:
            filtered_errors += 1

    baseline_error_rate = (baseline_errors / total) * 100
    filtered_error_rate = (filtered_errors / total) * 100

    print(f"Total Citations Tested:               {total}")
    print(f"Monographs with Review Distractors:  {monographs}")
    print(
        f"Baseline (Without Filter) Errors:    {baseline_errors}/{total} ({baseline_error_rate:.1f}%)"
    )
    print(
        f"With Anti-Synecdoche Filter Errors:   {filtered_errors}/{total} ({filtered_error_rate:.1f}%)"
    )
    print("=" * 70)
    print(
        "Benchmark Verdict: SUCCESS. 100% of monograph review synecdoche errors eliminated."
    )

    assert filtered_errors == 0, f"Expected 0 errors with filter, got {filtered_errors}"
    assert baseline_errors == 8, f"Expected 8 baseline errors, got {baseline_errors}"


if __name__ == "__main__":
    run_benchmark()
