from prompt_systematic_review.paperSource import Paper
from prompt_systematic_review.arxiv_source import ArXivSource
from prompt_systematic_review.ieee_source import IEEESource
from prompt_systematic_review.semantic_scholar_source import SemanticScholarSource
from datetime import date, datetime
from prompt_systematic_review.utils import process_paper_title
import pytest


def test_paper():
    paper1 = Paper(
        "How to write a paper",
        "Harry Parnasus",
        "example.com",
        date(2000, 2, 2),
        ["keyword1", "keyword2"],
        "amongus babongus",
    )
    paper2 = Paper(
        "How to NOT write a paper",
        "John Dickenson",
        "example.com",
        date(2002, 3, 3),
        ["keyword1", "keyword2"],
        "amongus babongus",
    )
    alsoPaper1 = Paper(
        "How to write a paper",
        "Dr. Harry Parnasus",
        "https://example2.com",
        date(2000, 2, 5),
        ["keyword1", "keyword2"],
        "amongus babongus",
    )

    assert paper1 == alsoPaper1
    assert paper1 != paper2 and paper2 != alsoPaper1


# mark as API_test, so it can be excluded by CI pipeline
@pytest.mark.API_test
def test_arxiv_source():
    # test that arXiv source returns papers properly
    arxiv_source = ArXivSource()
    papers = arxiv_source.getPapers(2, ["machine learning"])
    assert len(papers) == 2
    for paper in papers:
        assert isinstance(paper, Paper)
        assert "machine learning" in paper.keywords
        paper_src = arxiv_source.getPaperSrc(paper)
        assert isinstance(paper_src, str)
        assert len(paper_src) > 0

    # test that arXiv source returns the exact information for one paper properly
    arxiv_source = ArXivSource()
    TITLE = "Foundational Models in Medical Imaging: A Comprehensive Survey and Future Vision"
    papers = arxiv_source.getPapers(1, [TITLE])
    paper = papers[0]
    assert process_paper_title(paper.title) == TITLE.lower()
    assert paper.firstAuthor == "Bobby Azad"
    assert paper.url == "http://arxiv.org/abs/2310.18689v1"

    date_string = "Sat, 28 Oct 2023 12:08:12 UTC"
    date_object = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %Z").date()
    assert paper.dateSubmitted == date_object
    assert paper.keywords == [
        "foundational models in medical imaging: a comprehensive survey and future vision"
    ]


@pytest.mark.API_test
def test_ieee_source():
    # test that IEEE source returns papers properly
    ieee_source = IEEESource()
    papers = ieee_source.getPapers(2, ["machine learning"])
    assert len(papers) == 2
    for paper in papers:
        assert isinstance(paper, Paper)
        assert isinstance(paper.url, str)
        assert len(paper.url) > 0

    # test that IEEE source returns the exact information for one paper properly
    ieee_source = IEEESource()
    KEYWORDS = "Large Language Models"
    papers = ieee_source.getPapers(1, [KEYWORDS])
    paper = papers[0]
    print(paper.title)
    assert paper.firstAuthor == "Qurat Ul Ain Ali"
    assert paper.url.startswith("https://ieeexplore.ieee.org/")

    date_object = date(2021, 10, 10)
    assert paper.dateSubmitted == date_object
    assert "scalability" in [kw.lower() for kw in paper.keywords]
    assert "java" in [kw.lower() for kw in paper.keywords]


@pytest.mark.API_test
def test_semantic_scholar_source():
    semantic_scholar_source = SemanticScholarSource()
    keywords = ["deep learning"]
    papers = semantic_scholar_source.getPapers(keyWords=keywords, count=2)
    assert len(papers) == 2
    for paper in papers:
        assert isinstance(paper, Paper)
        assert keywords[0] in paper.keywords
        assert isinstance(paper.title, str)
        assert isinstance(paper.firstAuthor, str)
        assert paper.url.startswith("https://api.semanticscholar.org/")
        assert isinstance(paper.dateSubmitted, date) or paper.dateSubmitted is None


@pytest.mark.API_test
def test_semantic_scholar_get_open_access_papers():
    semantic_scholar = SemanticScholarSource()
    papers = semantic_scholar.getOpenAccessPapers(keyWords=["deep learning"], n=5)
    assert len(papers) == 5
    for paper in papers:
        assert semantic_scholar.getPaperPDF(paper.url.split("/")[-1]) is not None
