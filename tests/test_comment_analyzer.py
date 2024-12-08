from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
from projet_kbd.comment_analyzer import CommentAnalyzer


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
    analyzer = CommentAnalyzer(sample_comments)

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
    Test the `sentiment_analysis` function to ensure sentiment polarity is
    calculated correctly.
    """
    # Create an instance of CommentAnalyzer
    analyzer = CommentAnalyzer(sample_comments)

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


def test_generate_word_frequencies(sample_comments, mock_engine):
    """
    Test the `generate_word_frequencies` function to ensure it properly
    handles database retrieval and word frequency computation.
    """
    analyzer = CommentAnalyzer(sample_comments)
    analyzer.clean_comments()

    # Mock reading an existing table and handling the exception
    # when the table does not exist
    with patch("pandas.read_sql_table") as mock_read_sql:
        mock_read_sql.return_value = pd.DataFrame(
            {"word": ["great", "recipe", "time"], "frequency": [3, 5, 2]}
        )
        frequencies = analyzer.generate_word_frequencies(mock_engine, 100)
        assert frequencies == {"great": 3, "recipe": 5, "time": 2}

        # Test case when the table does not exist
        # and frequencies need to be computed
        mock_read_sql.side_effect = Exception("Table not found")
        # Assume compute method inside this function if no table is found
        frequencies = analyzer.generate_word_frequencies(mock_engine, 100)
        assert frequencies
        # check if dictionary is not empty, specifics
        # depend on actual cleaning and processing logic


def test_generate_word_frequencies_time(sample_comments, mock_engine):
    """
    Test the `generate_word_frequencies_associated_to_time` function to ensure
    it captures context correctly and computes frequencies based on that
    context.
    """
    analyzer = CommentAnalyzer(sample_comments)
    analyzer.clean_comments()
    # Assuming there is a method that cleans comments

    with patch("pandas.read_sql_table") as mock_read_sql:
        mock_read_sql.return_value = pd.DataFrame(
            {
                "phrase": ["time to cook", "save me so much time"],
                "frequency": [1, 1],
            }
        )
        frequencies = analyzer.generate_word_frequencies_associated_to_time(
            mock_engine, 10
        )
        assert frequencies == {"time to cook": 1, "save me so much time": 1}

        # Test when no existing data is found
        mock_read_sql.side_effect = Exception("Table not found")
        frequencies = analyzer.generate_word_frequencies_associated_to_time(
            mock_engine, 10
        )
        assert frequencies
        # Verify that it's computing something correctly,
        # details depend on method's logic
