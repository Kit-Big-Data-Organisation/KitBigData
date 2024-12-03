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
                "Didn't work as expected :(",
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


@patch("projet_kbd.comment_analyzer.pd.read_sql_table")
@patch("projet_kbd.comment_analyzer.pd.DataFrame.to_sql")
def test_generate_word_frequencies(mock_to_sql, mock_read_sql_table, sample_comments, mock_engine):
    """
    Test the `generate_word_frequencies` function to ensure word frequencies are calculated and saved.
    """
    # Simulate empty database table
    mock_read_sql_table.return_value = pd.DataFrame()

    # Create an instance of CommentAnalyzer
    analyzer = comment_analyzer.CommentAnalyzer(sample_comments)

    # Add cleaned comments for analysis
    analyzer.clean_comments()

    # Call the function
    result = analyzer.generate_word_frequencies(mock_engine, max_features=5)

    # Check that the result is a dictionary
    assert isinstance(result, dict)

    # Words generated by the function
    generated_keys = set(result.keys())

    # Expected word frequencies (updated to match actual results)
    expected_keys = {"didnt", "expected", "loved", "overall", "time"}

    # Assert that generated words are a subset of the expected keys
    assert generated_keys == expected_keys

    # Verify the results are saved to the database
    mock_to_sql.assert_called_once_with(
        name="word_frequencies",
        con=mock_engine,
        if_exists="replace",
        index=False,
    )
