from projet_kbd import utils
import sqlite3
import pandas as pd
import pytest


def test_determine_cuisine():
    """
    Test the `determine_cuisine` function.

    This test ensures that the function correctly determines the cuisine based
    on the provided tags.

    Assertions
    ----------
    - The function returns the correct cuisine for known tags.
    - The function returns the first matching cuisine when multiple cuisines
      are present.
    - The function returns "other" when no matching cuisines are found.
    - The function returns "other" for empty tags.
    - The function correctly identifies newly added cuisines.
    """
    # Test with tags matching known cuisines
    assert utils.determine_cuisine(["asian", "noodle"]) == "asian"
    assert utils.determine_cuisine(["taco", "mexican"]) == "mexican"

    # Test with multiple cuisines, should return the first match found
    assert utils.determine_cuisine(["asian", "mexican"]) == "asian"

    # Test with no matching cuisines
    assert utils.determine_cuisine(["german", "british"]) == "other"

    # Test with empty tags
    assert utils.determine_cuisine([]) == "other"

    # Additional tests for newly added cuisines
    assert utils.determine_cuisine(["french"]) == "french"
    assert utils.determine_cuisine(["indian", "curry"]) == "indian"


def test_highlight_cells():
    """
    Test the `highlight_cells` function.

    This test ensures that the function correctly applies the appropriate
    background color based on the ingredient.

    Assertions
    ----------
    - The function returns the correct background color for known ingredients.
    - The function returns an empty string for ingredients that should not be
      highlighted.
    """
    assert utils.highlight_cells("parmesan cheese") == "background-color: red"
    assert utils.highlight_cells("olive oil") == "background-color: lightgreen"
    assert utils.highlight_cells("chili powder") == "background-color: orange"
    assert (
        utils.highlight_cells("flour tortillas") == "background-color: orange"
    )
    assert (
        utils.highlight_cells("feta cheese") == "background-color: lightblue"
    )
    assert (
        utils.highlight_cells("dried oregano") == "background-color: lightblue"
    )
    assert utils.highlight_cells("soy sauce") == "background-color: lightpink"
    # Test a value that should not highlight
    assert utils.highlight_cells("water") == ""


@pytest.fixture
def sample_top_tags():
    """
    Provide sample top tags data for testing.

    Returns
    -------
    dict
        A dictionary containing sample top tags data.
    """
    return {
        0: {
            2002: (["tag1", "tag2"], [10.0, 20.0]),
            2003: (["tag3", "tag4"], [15.0, 25.0]),
        },
        1: {
            2002: (["tag5", "tag6"], [5.0, 30.0]),
            2003: (["tag7", "tag8"], [8.0, 18.0]),
        },
    }


@pytest.fixture
def mock_db_path(tmp_path):
    """
    Create a temporary SQLite database for testing.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Temporary directory provided by pytest.

    Returns
    -------
    str
        The path to the temporary SQLite database.
    """
    db_path = tmp_path / "test.db"
    return str(db_path)


def test_create_top_tags_database(mock_db_path, sample_top_tags):
    """
    Test the `create_top_tags_database` function.

    This test ensures that the function correctly creates and populates the
    top tags database.

    Parameters
    ----------
    mock_db_path : str
        The path to the temporary SQLite database.
    sample_top_tags : dict
        Sample top tags data for testing.

    Assertions
    ----------
    - The database contains the expected top tags data.
    """
    # Call the function
    utils.create_top_tags_database(mock_db_path, sample_top_tags)

    # Validate the database content
    conn = sqlite3.connect(mock_db_path)
    query = "SELECT * FROM top_tags"
    result = pd.read_sql_query(query, conn)
    conn.close()

    # Expected Result
    expected_data = [
        (0, 2002, "tag1", 10.0),
        (0, 2002, "tag2", 20.0),
        (0, 2003, "tag3", 15.0),
        (0, 2003, "tag4", 25.0),
        (1, 2002, "tag5", 5.0),
        (1, 2002, "tag6", 30.0),
        (1, 2003, "tag7", 8.0),
        (1, 2003, "tag8", 18.0),
    ]
    expected_df = pd.DataFrame(
        expected_data, columns=["set_number", "year", "label", "size"]
    )

    # Assert the results
    pd.testing.assert_frame_equal(result, expected_df)
