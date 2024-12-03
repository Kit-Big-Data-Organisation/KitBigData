from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
from projet_kbd import comment_analyzer


@pytest.fixture
def sample_comments():
    """
    Fixture providing a sample DataFrame for testing.
    """
    return pd.DataFrame(
        {
            "review": [
                "Great recipe! Loved it.",
                "Didn't work as expected :",
                "This recipe saved me so much time, thanks!",
                "Too salty for my taste, but overall good.",
                "Perfect recipe! Took some time but worth it.",
            ]
        }
    )


@pytest.fixture
def mock_engine():
    """
    Mock SQLAlchemy engine for database interactions.
    """
    return MagicMock()


def test_clean_comments(sample_comments):
    """
    Test the `clean_comments` function to ensure proper cleaning of comments.
    """
    # Create an instance of CommentAnalyzer
    analyzer = comment_analyzer.CommentAnalyzer(sample_comments)

    # Call the function
    analyzer.clean_comments()

    # Expected results
    expected_cleaned = [
        "great recipe loved it",
        "didnt work as expected",
        "this recipe saved me so much time thanks",
        "too salty for my taste but overall good",
        "perfect recipe took some time but worth it",
    ]

    # Assert the cleaned column is added and matches expectations
    assert "cleaned" in analyzer.comments.columns
    assert analyzer.comments["cleaned"].tolist() == expected_cleaned


def test_sentiment_analysis(sample_comments):
    """
    Test the `sentiment_analysis` function to ensure sentiment polarity is calculated correctly.
    """
    # Create an instance of CommentAnalyzer
    analyzer = comment_analyzer.CommentAnalyzer(sample_comments)

    # Add a cleaned column for analysis
    analyzer.clean_comments()

    # Call the function
    result = analyzer.sentiment_analysis()

    # Assert the polarity column is added
    assert "polarity" in result.columns

    # Assert the polarity values are correctly calculated (some examples)
    polarities = result["polarity"].tolist()
    assert polarities[0] > 0  # Positive comment
    assert polarities[1] < 0  # Negative comment
    assert polarities[2] > 0  # Positive comment

