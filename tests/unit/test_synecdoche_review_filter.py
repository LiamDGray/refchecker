from refchecker.utils.text_utils import find_best_match, is_book_review


def test_is_book_review_detection():
    assert is_book_review("Book Reviews: The Origins of Totalitarianism") is True
    assert (
        is_book_review("Book Review: The Disempowered: Illfare in Jobless America")
        is True
    )
    assert is_book_review("Review of Discipline and Punish") is True
    assert is_book_review("Reviewed Work: The Road to Serfdom by F. A. Hayek") is True
    assert is_book_review("Essay Review: Science in History") is True
    assert is_book_review("Review Article: Modern Social Theory") is True

    # Non-reviews
    assert is_book_review("The Origins of Totalitarianism") is False
    assert is_book_review("Discipline and Punish: The Birth of the Prison") is False
    assert is_book_review("A Review of Deep Learning Methods") is False
    assert is_book_review("Peer Review in Academic Publishing") is False
    assert is_book_review("") is False
    assert is_book_review(None) is False


def test_find_best_match_rejects_book_review_for_monograph():
    cleaned_title = "The Origins of Totalitarianism"
    authors = ["Hannah Arendt"]
    year = 1951

    candidates = [
        {
            "title": "Book Reviews : The Origins of Totalitarianism. By Hannah Arendt",
            "authors": ["G. E. G. Catlin"],
            "year": 1952,
            "type": "journal-article",
        },
        {
            "title": "The Origins of Totalitarianism",
            "authors": ["Hannah Arendt"],
            "year": 1951,
            "type": "book",
        },
    ]

    best_match, _ = find_best_match(
        candidates, cleaned_title, year=year, authors=authors
    )
    assert best_match is not None
    assert best_match["title"] == "The Origins of Totalitarianism"
    assert best_match["authors"] == ["Hannah Arendt"]


def test_find_best_match_skips_review_when_only_candidate():
    cleaned_title = "The Disempowered: Illfare in Jobless America"
    authors = ["Loic Wacquant"]

    candidates = [
        {
            "title": "Review of The Disempowered: Illfare in Jobless America",
            "authors": ["David Harvey"],
            "year": 2010,
            "type": "journal-article",
        }
    ]

    best_match, score = find_best_match(candidates, cleaned_title, authors=authors)
    # Should reject the review candidate rather than accepting reviewer as author
    assert best_match is None or score <= 0.0


def test_find_best_match_allows_review_when_cited_work_is_review():
    cleaned_title = "Review of Discipline and Punish"
    authors = ["David Garland"]

    candidates = [
        {
            "title": "Review of Discipline and Punish",
            "authors": ["David Garland"],
            "year": 1978,
            "type": "journal-article",
        }
    ]

    best_match, _ = find_best_match(candidates, cleaned_title, authors=authors)
    assert best_match is not None
    assert best_match["authors"] == ["David Garland"]
