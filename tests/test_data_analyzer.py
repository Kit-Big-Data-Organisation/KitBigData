from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

from projet_kbd import data_analyzer


@pytest.fixture
def mock_engine():
    """Mock l'objet SQLAlchemy engine."""
    return MagicMock()


@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6, 7],
            "year": [2005, 2005, 2007, 2007, 2009, 2010, 2010],
            "tags": [
                "['30-minutes-or-less', 'main-dish']",  # Rapide, main-dish
                "['4-hours-or-less', 'soups-stews']",  # Non rapide, soups-stews
                "['15-minutes-or-less', 'desserts']",  # Rapide, desserts
                "['60-minutes-or-less', 'appetizers']",  # Non rapide, appetizers
                "['15-minutes-or-less', 'salads']",  # Rapide, salads
                "['4-hours-or-less', 'side-dishes']",  # Non rapide, side-dishes
                "['30-minutes-or-less', 'snacks']",  # Rapide, snacks
            ],
            "interactions": ["abc", "abc", "abc", "abc", "abc", 100, 200],
        }
    )


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
def test_proportion_quick_recipe(
    mock_to_sql, mock_read_sql_table, sample_data, mock_engine
):
    """
    Test the `proportion_quick_recipe` function from the `data_analyzer` module.

    This test verifies the behavior of the `proportion_quick_recipe` function when:
    1. The database table is empty, forcing the function to calculate the proportions.
    2. The function processes the provided sample data to compute the expected output.
    3. The function saves the results correctly to the database.

    Steps tested:
    - Mocking database interactions (`read_sql_table` and `to_sql`).
    - Validating the structure of the output DataFrame.
    - Ensuring data is saved to the database with the correct parameters.

    Mocks:
    -------
    - `pd.read_sql_table`: Simulates an empty database table.
    - `pd.DataFrame.to_sql`: Verifies that the calculated results are saved to the database.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mocked version of `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mocked version of `pd.read_sql_table` to simulate reading from an empty database table.
    sample_data : pd.DataFrame (fixture)
        Sample data used for testing the function. Contains realistic test data.
    mock_engine : MagicMock (fixture)
        Mocked database engine used to simulate database connections.

    Returns
    -------
    None
        This test does not return any value but validates the function's behavior.

    Assertions
    ----------
    - Ensures the output DataFrame contains the expected columns: `Year` and `Proportion`.
    - Confirms that the function attempts to save the results to the database table `quick_recipe_proportion_table`.

    Raises
    ------
    AssertionError
        If the output structure or database interactions do not match the expected behavior.
    """
    # Simuler une base de données vide pour forcer le calcul
    mock_read_sql_table.return_value = pd.DataFrame()

    # Créer une instance avec des données fictives
    analyzer = data_analyzer.DataAnalyzer(data=sample_data)

    # Appeler la fonction
    result = analyzer.proportion_quick_recipe(mock_engine)

    # Vérifier que le DataFrame de résultat contient les colonnes attendues
    assert "Year" in result.columns
    assert "Proportion" in result.columns

    # Vérifier que les données sont sauvegardées dans la base
    mock_to_sql.assert_called_once_with(
        name="quick_recipe_proportion_table",
        con=mock_engine,
        if_exists="replace",
    )


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
def test_proportion_quick_recipe_calculation(
    mock_to_sql, mock_read_sql_table, sample_data, mock_engine
):
    """
    Test the `proportion_quick_recipe` function.

    This test ensures the function calculates the proportion of quick recipes
    relative to relevant recipes per year, correctly handles missing database data,
    and stores the results in the database.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from an empty database table.
    sample_data : pd.DataFrame
        Fixture containing realistic sample data for testing.
    mock_engine : MagicMock
        Mock database engine to simulate database connections.

    Assertions
    ----------
    - The resulting DataFrame matches the expected proportions for each year.
    - The function writes the results to the database table `quick_recipe_proportion_table`.
    """
    # Simulate an empty database table to force calculation
    mock_read_sql_table.return_value = pd.DataFrame()

    # Create a DataAnalyzer instance
    analyzer = data_analyzer.DataAnalyzer(sample_data)

    # Call the function
    result = analyzer.proportion_quick_recipe(mock_engine)

    # Expected proportions
    expected = pd.DataFrame(
        {
            "Year": [2005, 2007, 2009, 2010],
            "Proportion": [50.0, 50.0, 100.0, 50.0],
        }
    )

    # Assert the output matches the expected DataFrame
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
def test_get_quick_recipe_interaction_rate(
    mock_to_sql, mock_read_sql_table, sample_data, mock_engine
):
    """
    Test the `get_quick_recipe_interaction_rate` function.

    This test ensures the function calculates the interaction rate for quick recipes
    relative to all interactions per year, handles missing database data,
    and stores the results in the database.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from an empty database table.
    sample_data : pd.DataFrame
        Fixture containing realistic sample data for testing.
    mock_engine : MagicMock
        Mock database engine to simulate database connections.

    Assertions
    ----------
    - The resulting DataFrame matches the expected interaction rates for each year.
    - The function writes the results to the database table `rate_interactions_for_quick_recipe`.
    """
    # Simulate an empty database table to force calculation
    mock_read_sql_table.return_value = pd.DataFrame()

    # Create a DataAnalyzer instance
    analyzer = data_analyzer.DataAnalyzer(sample_data)

    # Call the function
    result = analyzer.get_quick_recipe_interaction_rate(mock_engine)

    # Expected interaction rates
    expected = pd.DataFrame(
        {
            "year": [2005, 2007, 2009, 2010],
            "Quick_Tag_Interactions": [1, 1, 1, 1],
            "Total_Interactions": [2, 2, 1, 2],
            "Proportion": [50.0, 50.0, 100.0, 50.0],
        }
    )

    # Assert the output matches the expected DataFrame
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
def test_get_categories_quick_recipe(
    mock_to_sql, mock_read_sql_table, sample_data, mock_engine
):
    """
    Test the `get_categories_quick_recipe` function.

    This test ensures the function calculates the counts of main categories
    for quick recipes, handles missing database data, and stores the results
    in the database.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from an empty database
        table.
    sample_data : pd.DataFrame
        Fixture containing realistic sample data for testing.
    mock_engine : MagicMock
        Mock database engine to simulate database connections.

    Assertions
    ----------
    - The resulting DataFrame matches the expected category counts for
    quick recipes.
    - The function writes the results to the database table
    `categories_quick_recipe`.
    """
    # Simulate an empty database table to force calculation
    mock_read_sql_table.return_value = pd.DataFrame()

    # Create a DataAnalyzer instance
    analyzer = data_analyzer.DataAnalyzer(sample_data)

    # Call the function
    result = analyzer.get_categories_quick_recipe(mock_engine)

    # Expected category counts
    expected = pd.DataFrame(
        {
            "Category": [
                "main-dish",
                "desserts",
                "appetizers",
                "soups-stews",
                "salads",
                "side-dishes",
                "snacks",
            ],
            "Count": [1, 1, 0, 0, 1, 0, 1],
        }
    )

    # Assert the output matches the expected DataFrame
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)
