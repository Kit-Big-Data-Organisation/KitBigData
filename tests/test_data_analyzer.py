from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
import sqlalchemy
from collections import Counter

from projet_kbd.data_analyzer import DataAnalyzer


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
            "submitted": [
                "2020-01-10",
                "2020-03-15",
                "2021-05-20",
                "2021-07-30",
                "2022-09-10",
                "2022-12-01",
                "2023-01-15",
            ],
            "date": [
                "2020-01-15",
                "2020-03-20",
                "2021-05-25",
                "2021-08-01",
                "2022-09-15",
                "2023-01-10",
                "2023-01-20",
            ],
            "rating": [4.0, 5.0, 3.0, 4.5, 5.0, 2.0, 3.5],
            "minutes": [30, 45, 15, 60, 20, 50, 25],
            "tags": [
                "['30-minutes-or-less', 'main-dish']",
                "['4-hours-or-less', 'soups-stews']",
                "['15-minutes-or-less', 'desserts']",
                "['60-minutes-or-less', 'appetizers']",
                "['15-minutes-or-less', 'salads']",
                "['4-hours-or-less', 'side-dishes']",
                "['30-minutes-or-less', 'snacks']",
            ],
            "n_steps": [1000, 1200, 800, 1000, 1500, 900, 1100],
            "interactions": ["abc", "abc", "abc", "abc", "abc", 100, 200],
        }
    )
def sample_data_oils():
    """
    Fixture providing sample data for oil analysis.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing sample data with columns 'id', 'year', and
        'ingredients'.
    """
    return pd.DataFrame(
        {
            'id': [1, 2, 3, 4],
            'year': [2002, 2002, 2003, 2003],
            'ingredients': ["['olive oil', 'salt']", 
                            "['vegetable oil', 'pepper']", 
                            "['olive oil', 'garlic']", 
                            "['extra virgin olive oil', 'pepper']"]
        })

@patch("projet_kbd.data_analyzer.pd.read_sql_table")
def test_analyze_oils_data_found_in_database(mock_read_sql_table):
    """
    Test the `analyze_oils` method when data is found in the database.

    This test ensures that the method correctly retrieves and returns the
    existing data from the database.

    Parameters
    ----------
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.

    Assertions
    ----------
    - The resulting DataFrame matches the mock data found in the database.
    - The function reads the data from the database table `oils_dataframe`.
    """
    # Simulate data being found in the database
    mock_existing_data = pd.DataFrame({
        'Year': [2002, 2003],
        'Oil Type': ['olive oil', 'vegetable oil'],
        'Proportion': [0.7, 0.3]
    })
    mock_read_sql_table.return_value = mock_existing_data

    # Initialize the analyzer
    analyzer = DataAnalyzer(data=sample_data_oils())

    # Call the method
    result = analyzer.analyze_oils(mock_engine)

    # Verify it returned the database data
    pd.testing.assert_frame_equal(result, mock_existing_data)
    mock_read_sql_table.assert_called_once_with('oils_dataframe', con=mock_engine)

    # Stop the mock
    patch.stopall()

def test_normalize_proportions():
    """
    Test the normalization of oil proportions per year.

    This test ensures that the proportions of different oils are correctly
    normalized for each year without modifying the original dictionary during
    iteration.

    Assertions
    ----------
    - The normalized proportions match the expected values for each year.
    """
    # Simulate internal normalization logic
    year_oil = {
        2002: {'olive oil': 3, 'vegetable oil': 1},
        2003: {'olive oil': 2, 'extra virgin olive oil': 2}
    }

    # Normalize proportions without modifying the dictionary while iterating
    normalized_year_oil = {}
    for year, oils in year_oil.items():
        total = sum(oils.values())
        normalized_year_oil[year] = {oil: count / total for oil, count in oils.items()}

    expected_normalized = {
        2002: {'olive oil': 0.75, 'vegetable oil': 0.25},
        2003: {'olive oil': 0.5, 'extra virgin olive oil': 0.5}
    }

    assert normalized_year_oil == expected_normalized


def test_group_interactions_year():
    """
    Test the `group_interactions_year` method.

    This test ensures that the method correctly groups interactions by year
    and counts the number of interactions per year.

    Assertions
    ----------
    - The indices of the resulting group match the expected years.
    - The values of the resulting group match the expected counts of reviews
      per year.
    """
    # Sample dataset
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "year": [2002, 2002, 2003, 2003, 2003],
        "review": ["Review1", "Review2", "Review3", "Review4", "Review5"]
    })

    # Initialize the analyzer with sample data
    analyzer = DataAnalyzer(data=sample_data)

    # Call the method
    indices, values = analyzer.group_interactions_year()

    # Expected output
    expected_indices = pd.Index([2002, 2003])  # Years with reviews
    expected_values = [2, 3]  # Review counts per year

    # Validate the output
    assert all(indices == expected_indices)
    assert all(values == expected_values)

def test_group_recipes_year():
    """
    Test the `group_recipes_year` method.

    This test ensures that the method correctly groups recipes by year and
    counts the number of unique recipes per year.

    Assertions
    ----------
    - The indices of the resulting group match the expected unique years.
    - The values of the resulting group match the expected counts of unique
      recipes per year.
    """
    # Sample dataset
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 1, 4, 5],  # Recipe IDs
        "year": [2002, 2002, 2003, 2003, 2003, 2004]  # Years
    })

    # Initialize the analyzer with sample data
    analyzer = DataAnalyzer(data=sample_data)

    # Call the method
    indices, values = analyzer.group_recipes_year()

    # Expected output
    expected_indices = pd.Index([2002, 2003, 2004])  # Unique years
    expected_values = [2, 3, 1]  # Unique recipe counts per year

    # Validate the output
    assert all(indices == expected_indices)
    assert all(values == expected_values)


def test_get_tags():
    """
    Test the `get_tags` method.

    This test ensures that the method correctly retrieves and counts the tags
    for recipes in a given year.

    Assertions
    ----------
    - The resulting Counter matches the expected tag counts for the specified
      year.
    """
    # Sample dataset
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "year": [2002, 2002, 2003, 2003],
        "tags": [
            "['quick', 'easy', 'main course']",
            "['quick', 'healthy', 'snack']",
            "['dessert', 'sweet']",
            "['healthy', 'snack', 'sweet']"
        ]
    })

    # Initialize the analyzer with sample data
    analyzer = DataAnalyzer(data=sample_data)

    # Call the method for the year 2002
    result = analyzer.get_tags(2002)

    # Expected output
    expected_tags = Counter({
        "quick": 2,
        "easy": 1,
        "main course": 1,
        "healthy": 1,
        "snack": 1
    })

    # Validate the result
    assert result == expected_tags


def test_get_top_tags():
    """
    Test the `get_top_tags` method.

    This test ensures that the method correctly retrieves and counts the top
    tags for recipes in a given year.

    Assertions
    ----------
    - The resulting dictionary matches the expected top tags and their counts
      for the specified year.
    """
    # Sample dataset
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "year": [2002, 2002, 2003, 2003],
        "tags": [
            "['quick', 'easy', 'main course']",
            "['quick', 'healthy', 'snack']",
            "['dessert', 'sweet']",
            "['healthy', 'snack', 'sweet']"
        ]
    })

    # Initialize the analyzer with sample data
    analyzer = DataAnalyzer(data=sample_data)

    # Call the method for the year 2002
    result = analyzer.get_top_tags(2002)

    # Expected output
    expected_top_tags = {
        2002: [
            ("quick", 2),
            ("easy", 1),
            ("main course", 1),
            ("healthy", 1),
            ("snack", 1)
        ]
    }

    # Validate the result
    assert result == expected_top_tags


@patch("projet_kbd.data_analyzer.utils.create_top_tags_database")
@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.DataAnalyzer.get_top_tags")
def test_get_top_tag_per_year(mock_get_top_tags, mock_read_sql_table, mock_create_db):
    """
    Test the `get_top_tag_per_year` method.

    This test ensures that the method correctly retrieves the top tags per
    year from the database, and creates the database table if it doesn't
    exist.

    Parameters
    ----------
    mock_get_top_tags : MagicMock
        Mock for `DataAnalyzer.get_top_tags` to simulate retrieving top tags.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.
    mock_create_db : MagicMock
        Mock for `utils.create_top_tags_database` to simulate creating the
        database table.

    Assertions
    ----------
    - The method reads the data from the database table `top_tags` if it
      exists.
    - The method does not recreate the table if data already exists.
    - The method creates the table if no data is found in the database.
    """
    # Simulate database table already existing
    mock_read_sql_table.return_value = pd.DataFrame({
        "set_number": [0, 0, 0],
        "year": [2002, 2003, 2004],
        "label": ["quick", "easy", "snack"],
        "size": [20, 15, 10]
    })

    # Initialize the analyzer
    analyzer = DataAnalyzer(data=pd.DataFrame())

    # Call the method with mock engine and database path
    engine = MagicMock()
    db_path = "test_path"
    result = analyzer.get_top_tag_per_year(engine, db_path)

    # Verify it doesn't recreate the table if data already exists
    mock_read_sql_table.assert_called_once_with("top_tags", con=engine)
    mock_create_db.assert_not_called()
    assert result is None

    # Simulate no data found in the database
    mock_read_sql_table.side_effect = Exception("No table found")
    mock_get_top_tags.side_effect = lambda year: {year: Counter({"tag1": 10, "tag2": 5, "tag3": 3}).most_common(10)}

    # Call the method again
    analyzer.get_top_tag_per_year(engine, db_path)

    # Verify table creation
    mock_create_db.assert_called_once()



@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
def test_analyze_cuisines(mock_to_sql, mock_read_sql_table):
    """
    Test the `analyze_cuisines` method.

    This test ensures that the method correctly analyzes the proportions of
    different cuisines in the dataset and handles cases where data is already
    present in the database or needs to be calculated and saved.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.

    Assertions
    ----------
    - The method returns the existing data if found in the database.
    - The method calculates and returns the correct proportions if no data is
      found in the database.
    - The method saves the calculated proportions to the database.
    """
    # Simulate data already in the database
    mock_read_sql_table.return_value = pd.DataFrame({
        "Cuisine": ["Italian", "American"],
        "Proportion": [0.3, 0.7]
    })

    # Initialize analyzer with sample data
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6],
        "cuisine": ["Italian", "American", "Mexican", "Mexican", "others", "Greek"]
    })
    analyzer = DataAnalyzer(data=sample_data)

    # Call the method with mock engine
    engine = MagicMock()
    result = analyzer.analyze_cuisines(engine)

    # Verify it returns the existing data if found in the database
    mock_read_sql_table.assert_called_once_with("cuisine_data", con=engine)
    pd.testing.assert_frame_equal(result, mock_read_sql_table.return_value)
    mock_to_sql.assert_not_called()

    # Simulate no data in the database
    mock_read_sql_table.side_effect = Exception("No table found")
    analyzer.data = sample_data  # Assign the test dataset again

    # Call the method to process and save data
    result = analyzer.analyze_cuisines(engine)

    # Expected processed data
    expected_result = pd.DataFrame({
        "Cuisine": ["Italian", "American", "Mexican", "Greek", "others"],
        "Proportion": [
            1 / 6,  # Italian
            1 / 6,  # American
            2 / 6,  # Mexican
            1 / 6,  # Greek
            1 / 6   # Others aggregated
        ]
    })

    # Verify the proportions are calculated correctly
    pd.testing.assert_frame_equal(result.sort_values(by="Cuisine").reset_index(drop=True),
                                   expected_result.sort_values(by="Cuisine").reset_index(drop=True))

    # Ensure the result is saved to the database
    mock_to_sql.assert_called_once_with(name="cuisine_data", con=engine, if_exists="replace")


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
@patch("projet_kbd.data_analyzer.utils.relevant_cuisines", ["Italian", "American", "Mexican", "Greek"])
def test_top_commun_ingredients(mock_to_sql, mock_read_sql_table):
    """
    Test the `top_commun_ingredients` method.

    This test ensures that the method correctly identifies and returns the top
    common ingredients for each relevant cuisine, and handles cases where data
    is already present in the database or needs to be calculated and saved.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.

    Assertions
    ----------
    - The method returns the existing data if found in the database.
    - The method calculates and returns the correct top common ingredients if
      no data is found in the database.
    - The method saves the calculated top common ingredients to the database.
    """
    # Simulate data already in the database
    mock_read_sql_table.return_value = pd.DataFrame({
        "cuisine": ["Italian", "American"],
        "Top ingredient 1": ["tomato", "bread"],
        "Top ingredient 2": ["cheese", "butter"],
        "Top ingredient 3": ["basil", "sugar"],
        "Top ingredient 4": ["olive oil", "milk"],
        "Top ingredient 5": ["garlic", "flour"]
    })

    # Initialize the analyzer with sample data
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6],
        "cuisine": ["Italian", "American", "Mexican", "Greek", "Mexican", "Italian"],
        "ingredients": [
            "['tomato', 'cheese', 'basil', 'olive oil', 'garlic']",
            "['bread', 'butter', 'sugar', 'milk', 'flour']",
            "['tortilla', 'beans', 'chili powder', 'corn', 'cheese']",
            "['olive oil', 'feta', 'oregano', 'lemon', 'cucumber']",
            "['tortilla', 'chili powder', 'avocado', 'cheese', 'tomato']",
            "['tomato', 'cheese', 'garlic', 'basil', 'olive oil']"
        ]
    })
    analyzer = DataAnalyzer(data=sample_data)

    # Mock engine
    engine = MagicMock()

    # Test case 1: Data already exists in the database
    result = analyzer.top_commun_ingredients(engine)

    # Verify it returns the existing data
    mock_read_sql_table.assert_called_once_with("cuisine_top_ingredients", con=engine)
    pd.testing.assert_frame_equal(result, mock_read_sql_table.return_value)
    mock_to_sql.assert_not_called()

    # Test case 2: Data missing in the database
    mock_read_sql_table.side_effect = Exception("No table found")

    # Call the method to process the data
    result = analyzer.top_commun_ingredients(engine)

    # Expected processed DataFrame
    expected_result = pd.DataFrame({
        "cuisine": ["American", "Greek", "Italian", "Mexican"],
        "Top ingredient 1": ["bread", "olive oil", "tomato", "tortilla"],
        "Top ingredient 2": ["butter", "feta", "cheese", "chili powder"],
        "Top ingredient 3": ["sugar", "oregano", "basil", "cheese"],
        "Top ingredient 4": ["milk", "lemon", "olive oil", "beans"],
        "Top ingredient 5": ["flour", "cucumber", "garlic", "corn"]
    })

    # Ensure consistent dtype for textual columns
    text_columns = ["cuisine", "Top ingredient 1", "Top ingredient 2", "Top ingredient 3", "Top ingredient 4", "Top ingredient 5"]
    for col in text_columns:
        result[col] = result[col].astype("string")
        expected_result[col] = expected_result[col].astype("string")

    # Validate the result structure and content
    pd.testing.assert_frame_equal(
        result.sort_values("cuisine").reset_index(drop=True),
        expected_result.sort_values("cuisine").reset_index(drop=True)
    )

    # Ensure the result is saved to the database
    mock_to_sql.assert_called_once_with(
        name="cuisine_top_ingredients",
        con=engine,
        if_exists="replace"
    )

@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
@patch("projet_kbd.data_analyzer.utils.relevant_cuisines", ["Italian", "American", "Mexican", "Greek"])
def test_cuisine_evolution(mock_to_sql, mock_read_sql_table):
    """
    Test the `cuisine_evolution` method.

    This test ensures that the method correctly analyzes the evolution of
    different cuisines over the years and handles cases where data is already
    present in the database or needs to be calculated and saved.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.

    Assertions
    ----------
    - The method returns the existing data if found in the database.
    - The method calculates and returns the correct evolution of cuisines if
      no data is found in the database.
    - The method saves the calculated evolution of cuisines to the database.
    """
    # Simulate data already in the database
    mock_read_sql_table.return_value = pd.DataFrame({
        "Year": [2002, 2003],
        "American": [50.0, 40.0],
        "Greek": [5.0, 5.0],
        "Italian": [30.0, 35.0],
        "Greek": [15.0, 20.0]
    }).set_index("Year")

    # Initialize the analyzer with sample data
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6],
        "cuisine": ["Italian", "American", "Mexican", "Greek", "Mexican", "Italian"],
        "year": [2002, 2002, 2003, 2003, 2003, 2003]
    })
    analyzer = DataAnalyzer(data=sample_data)

    # Mock SQLAlchemy engine
    engine = MagicMock()

    # Test case 1: Data already exists in the database
    result = analyzer.cuisine_evolution(engine)

    # Validate it returns the existing database data
    mock_read_sql_table.assert_called_once_with("cuisine_evolution_dataframe", con=engine)
    pd.testing.assert_frame_equal(result, mock_read_sql_table.return_value)
    mock_to_sql.assert_not_called()

    # Test case 2: Data not found in the database
    mock_read_sql_table.side_effect = Exception("No table found")

    # Call the method to process the data
    result = analyzer.cuisine_evolution(engine)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)

    # Expected processed DataFrame
    expected_result = pd.DataFrame({
        "Cuisine": ["American", "Greek", "Italian", "Mexican"],
        2002: [50.0, 0.0, 50.0, 0.0],
        2003: [0.0, 25.0, 25.0, 50.0],
        2004: [0.0, 0.0, 0.0, 0.0],
        2005: [0.0, 0.0, 0.0, 0.0],
        2006: [0.0, 0.0, 0.0, 0.0],
        2007: [0.0, 0.0, 0.0, 0.0],
        2008: [0.0, 0.0, 0.0, 0.0],
        2009: [0.0, 0.0, 0.0, 0.0],
        2010: [0.0, 0.0, 0.0, 0.0]
    }).set_index("Cuisine").T

    expected_result = expected_result.reset_index().rename(columns={"index": "Year"}).set_index("Year")
    expected_result.columns.name = "Cuisine"

    # Updated validation
    pd.testing.assert_frame_equal(
        result,
        expected_result
    )

    # Ensure the result is saved to the database
    mock_to_sql.assert_called_once_with(
        name="cuisine_evolution_dataframe",
        con=engine,
        if_exists="replace",
        index=True,
        index_label="Year"
    )


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
@patch("projet_kbd.data_analyzer.utils.relevant_cuisines", ["Italian", "American", "Mexican", "Greek"])
def test_analyse_cuisine_nutritions(mock_to_sql, mock_read_sql_table):
    """
    Test the `analyse_cuisine_nutritions` method.

    This test ensures that the method correctly analyzes the nutritional
    information of different cuisines and handles cases where data is already
    present in the database or needs to be calculated and saved.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.

    Assertions
    ----------
    - The method returns the existing data if found in the database.
    - The method calculates and returns the correct nutritional information if
      no data is found in the database.
    - The method saves the calculated nutritional information to the database.
    """
    # Simulate data already in the database
    mock_read_sql_table.return_value = pd.DataFrame({
        "cuisine": ["Italian", "American"],
        "sugar": [5.0, 4.5],
        "protein": [10.0, 8.5],
        "carbs": [40.0, 35.0],
        "totalFat": [20.0, 18.0],
        "satFat": [8.0, 6.0],
        "sodium": [500.0, 450.0],
        "cal": [300.0, 280.0],
        "minutes": [30.0, 25.0]
    })

    # Initialize the analyzer with sample data
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "cuisine": ["Italian", "American", "Mexican", "Greek"],
        "sugar": [5.0, 4.5, 6.0, 3.0],
        "protein": [10.0, 8.5, 12.0, 9.0],
        "carbs": [40.0, 35.0, 50.0, 30.0],
        "totalFat": [20.0, 18.0, 25.0, 15.0],
        "satFat": [8.0, 6.0, 10.0, 4.0],
        "sodium": [500.0, 450.0, 600.0, 400.0],
        "cal": [300.0, 280.0, 350.0, 250.0],
        "minutes": [30.0, 25.0, 40.0, 20.0]
    })
    analyzer = DataAnalyzer(data=sample_data)

    # Mock engine
    engine = MagicMock()

    # Test case 1: Data already exists in the database
    result = analyzer.analyse_cuisine_nutritions(engine)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)

    # Validate it returns the existing database data
    mock_read_sql_table.assert_called_once_with("cuisines_nutritions", con=engine)
    pd.testing.assert_frame_equal(result, mock_read_sql_table.return_value)
    mock_to_sql.assert_not_called()

    # Test case 2: Data not found in the database
    mock_read_sql_table.side_effect = Exception("No table found")

    # Call the method to process the data
    result = analyzer.analyse_cuisine_nutritions(engine)

    # Expected processed DataFrame
    expected_result = pd.DataFrame({
        "sugar": [4.5, 3.0, 5.0, 6.0],
        "protein": [8.5, 9.0, 10.0, 12.0],
        "carbs": [35.0, 30.0, 40.0, 50.0],
        "totalFat": [18.0, 15.0, 20.0, 25.0],
        "satFat": [6.0, 4.0, 8.0, 10.0],
        "sodium": [450.0, 400.0, 500.0, 600.0],
        "cal": [280.0, 250.0, 300.0, 350.0],
        "minutes": [25.0, 20.0, 30.0, 40.0],
    }, index=["American", "Greek", "Italian", "Mexican"])

    expected_result.index.name = "cuisine"

    # Validate the result structure and content
    pd.testing.assert_frame_equal(
        result.sort_index(),
        expected_result.sort_index()
    )

    # Ensure the result is saved to the database
    mock_to_sql.assert_called_once_with(
        name="cuisines_nutritions",
        con=engine,
        if_exists="replace"
    )
def sample_data_oils():
    """
    Fixture providing sample data for oil analysis.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing sample data with columns 'id', 'year', and
        'ingredients'.
    """
    return pd.DataFrame(
        {
            'id': [1, 2, 3, 4],
            'year': [2002, 2002, 2003, 2003],
            'ingredients': ["['olive oil', 'salt']", 
                            "['vegetable oil', 'pepper']", 
                            "['olive oil', 'garlic']", 
                            "['extra virgin olive oil', 'pepper']"]
        })

@patch("projet_kbd.data_analyzer.pd.read_sql_table")
def test_analyze_oils_data_found_in_database(mock_read_sql_table):
    """
    Test the `analyze_oils` method when data is found in the database.

    This test ensures that the method correctly retrieves and returns the
    existing data from the database.

    Parameters
    ----------
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.

    Assertions
    ----------
    - The resulting DataFrame matches the mock data found in the database.
    - The function reads the data from the database table `oils_dataframe`.
    """
    # Simulate data being found in the database
    mock_existing_data = pd.DataFrame({
        'Year': [2002, 2003],
        'Oil Type': ['olive oil', 'vegetable oil'],
        'Proportion': [0.7, 0.3]
    })
    mock_read_sql_table.return_value = mock_existing_data

    # Initialize the analyzer
    analyzer = DataAnalyzer(data=sample_data_oils())

    # Call the method
    result = analyzer.analyze_oils(mock_engine)

    # Verify it returned the database data
    pd.testing.assert_frame_equal(result, mock_existing_data)
    mock_read_sql_table.assert_called_once_with('oils_dataframe', con=mock_engine)

    # Stop the mock
    patch.stopall()

def test_normalize_proportions():
    """
    Test the normalization of oil proportions per year.

    This test ensures that the proportions of different oils are correctly
    normalized for each year without modifying the original dictionary during
    iteration.

    Assertions
    ----------
    - The normalized proportions match the expected values for each year.
    """
    # Simulate internal normalization logic
    year_oil = {
        2002: {'olive oil': 3, 'vegetable oil': 1},
        2003: {'olive oil': 2, 'extra virgin olive oil': 2}
    }

    # Normalize proportions without modifying the dictionary while iterating
    normalized_year_oil = {}
    for year, oils in year_oil.items():
        total = sum(oils.values())
        normalized_year_oil[year] = {oil: count / total for oil, count in oils.items()}

    expected_normalized = {
        2002: {'olive oil': 0.75, 'vegetable oil': 0.25},
        2003: {'olive oil': 0.5, 'extra virgin olive oil': 0.5}
    }

    assert normalized_year_oil == expected_normalized


def test_group_interactions_year():
    """
    Test the `group_interactions_year` method.

    This test ensures that the method correctly groups interactions by year
    and counts the number of interactions per year.

    Assertions
    ----------
    - The indices of the resulting group match the expected years.
    - The values of the resulting group match the expected counts of reviews
      per year.
    """
    # Sample dataset
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "year": [2002, 2002, 2003, 2003, 2003],
        "review": ["Review1", "Review2", "Review3", "Review4", "Review5"]
    })

    # Initialize the analyzer with sample data
    analyzer = DataAnalyzer(data=sample_data)

    # Call the method
    indices, values = analyzer.group_interactions_year()

    # Expected output
    expected_indices = pd.Index([2002, 2003])  # Years with reviews
    expected_values = [2, 3]  # Review counts per year

    # Validate the output
    assert all(indices == expected_indices)
    assert all(values == expected_values)

def test_group_recipes_year():
    """
    Test the `group_recipes_year` method.

    This test ensures that the method correctly groups recipes by year and
    counts the number of unique recipes per year.

    Assertions
    ----------
    - The indices of the resulting group match the expected unique years.
    - The values of the resulting group match the expected counts of unique
      recipes per year.
    """
    # Sample dataset
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 1, 4, 5],  # Recipe IDs
        "year": [2002, 2002, 2003, 2003, 2003, 2004]  # Years
    })

    # Initialize the analyzer with sample data
    analyzer = DataAnalyzer(data=sample_data)

    # Call the method
    indices, values = analyzer.group_recipes_year()

    # Expected output
    expected_indices = pd.Index([2002, 2003, 2004])  # Unique years
    expected_values = [2, 3, 1]  # Unique recipe counts per year

    # Validate the output
    assert all(indices == expected_indices)
    assert all(values == expected_values)


def test_get_tags():
    """
    Test the `get_tags` method.

    This test ensures that the method correctly retrieves and counts the tags
    for recipes in a given year.

    Assertions
    ----------
    - The resulting Counter matches the expected tag counts for the specified
      year.
    """
    # Sample dataset
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "year": [2002, 2002, 2003, 2003],
        "tags": [
            "['quick', 'easy', 'main course']",
            "['quick', 'healthy', 'snack']",
            "['dessert', 'sweet']",
            "['healthy', 'snack', 'sweet']"
        ]
    })

    # Initialize the analyzer with sample data
    analyzer = DataAnalyzer(data=sample_data)

    # Call the method for the year 2002
    result = analyzer.get_tags(2002)

    # Expected output
    expected_tags = Counter({
        "quick": 2,
        "easy": 1,
        "main course": 1,
        "healthy": 1,
        "snack": 1
    })

    # Validate the result
    assert result == expected_tags


def test_get_top_tags():
    """
    Test the `get_top_tags` method.

    This test ensures that the method correctly retrieves and counts the top
    tags for recipes in a given year.

    Assertions
    ----------
    - The resulting dictionary matches the expected top tags and their counts
      for the specified year.
    """
    # Sample dataset
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "year": [2002, 2002, 2003, 2003],
        "tags": [
            "['quick', 'easy', 'main course']",
            "['quick', 'healthy', 'snack']",
            "['dessert', 'sweet']",
            "['healthy', 'snack', 'sweet']"
        ]
    })

    # Initialize the analyzer with sample data
    analyzer = DataAnalyzer(data=sample_data)

    # Call the method for the year 2002
    result = analyzer.get_top_tags(2002)

    # Expected output
    expected_top_tags = {
        2002: [
            ("quick", 2),
            ("easy", 1),
            ("main course", 1),
            ("healthy", 1),
            ("snack", 1)
        ]
    }

    # Validate the result
    assert result == expected_top_tags


@patch("projet_kbd.data_analyzer.utils.create_top_tags_database")
@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.DataAnalyzer.get_top_tags")
def test_get_top_tag_per_year(mock_get_top_tags, mock_read_sql_table, mock_create_db):
    """
    Test the `get_top_tag_per_year` method.

    This test ensures that the method correctly retrieves the top tags per
    year from the database, and creates the database table if it doesn't
    exist.

    Parameters
    ----------
    mock_get_top_tags : MagicMock
        Mock for `DataAnalyzer.get_top_tags` to simulate retrieving top tags.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.
    mock_create_db : MagicMock
        Mock for `utils.create_top_tags_database` to simulate creating the
        database table.

    Assertions
    ----------
    - The method reads the data from the database table `top_tags` if it
      exists.
    - The method does not recreate the table if data already exists.
    - The method creates the table if no data is found in the database.
    """
    # Simulate database table already existing
    mock_read_sql_table.return_value = pd.DataFrame({
        "set_number": [0, 0, 0],
        "year": [2002, 2003, 2004],
        "label": ["quick", "easy", "snack"],
        "size": [20, 15, 10]
    })

    # Initialize the analyzer
    analyzer = DataAnalyzer(data=pd.DataFrame())

    # Call the method with mock engine and database path
    engine = MagicMock()
    db_path = "test_path"
    result = analyzer.get_top_tag_per_year(engine, db_path)

    # Verify it doesn't recreate the table if data already exists
    mock_read_sql_table.assert_called_once_with("top_tags", con=engine)
    mock_create_db.assert_not_called()
    assert result is None

    # Simulate no data found in the database
    mock_read_sql_table.side_effect = Exception("No table found")
    mock_get_top_tags.side_effect = lambda year: {year: Counter({"tag1": 10, "tag2": 5, "tag3": 3}).most_common(10)}

    # Call the method again
    analyzer.get_top_tag_per_year(engine, db_path)

    # Verify table creation
    mock_create_db.assert_called_once()



@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
def test_analyze_cuisines(mock_to_sql, mock_read_sql_table):
    """
    Test the `analyze_cuisines` method.

    This test ensures that the method correctly analyzes the proportions of
    different cuisines in the dataset and handles cases where data is already
    present in the database or needs to be calculated and saved.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.

    Assertions
    ----------
    - The method returns the existing data if found in the database.
    - The method calculates and returns the correct proportions if no data is
      found in the database.
    - The method saves the calculated proportions to the database.
    """
    # Simulate data already in the database
    mock_read_sql_table.return_value = pd.DataFrame({
        "Cuisine": ["Italian", "American"],
        "Proportion": [0.3, 0.7]
    })

    # Initialize analyzer with sample data
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6],
        "cuisine": ["Italian", "American", "Mexican", "Mexican", "others", "Greek"]
    })
    analyzer = DataAnalyzer(data=sample_data)

    # Call the method with mock engine
    engine = MagicMock()
    result = analyzer.analyze_cuisines(engine)

    # Verify it returns the existing data if found in the database
    mock_read_sql_table.assert_called_once_with("cuisine_data", con=engine)
    pd.testing.assert_frame_equal(result, mock_read_sql_table.return_value)
    mock_to_sql.assert_not_called()

    # Simulate no data in the database
    mock_read_sql_table.side_effect = Exception("No table found")
    analyzer.data = sample_data  # Assign the test dataset again

    # Call the method to process and save data
    result = analyzer.analyze_cuisines(engine)

    # Expected processed data
    expected_result = pd.DataFrame({
        "Cuisine": ["Italian", "American", "Mexican", "Greek", "others"],
        "Proportion": [
            1 / 6,  # Italian
            1 / 6,  # American
            2 / 6,  # Mexican
            1 / 6,  # Greek
            1 / 6   # Others aggregated
        ]
    })

    # Verify the proportions are calculated correctly
    pd.testing.assert_frame_equal(result.sort_values(by="Cuisine").reset_index(drop=True),
                                   expected_result.sort_values(by="Cuisine").reset_index(drop=True))

    # Ensure the result is saved to the database
    mock_to_sql.assert_called_once_with(name="cuisine_data", con=engine, if_exists="replace")


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
@patch("projet_kbd.data_analyzer.utils.relevant_cuisines", ["Italian", "American", "Mexican", "Greek"])
def test_top_commun_ingredients(mock_to_sql, mock_read_sql_table):
    """
    Test the `top_commun_ingredients` method.

    This test ensures that the method correctly identifies and returns the top
    common ingredients for each relevant cuisine, and handles cases where data
    is already present in the database or needs to be calculated and saved.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.

    Assertions
    ----------
    - The method returns the existing data if found in the database.
    - The method calculates and returns the correct top common ingredients if
      no data is found in the database.
    - The method saves the calculated top common ingredients to the database.
    """
    # Simulate data already in the database
    mock_read_sql_table.return_value = pd.DataFrame({
        "cuisine": ["Italian", "American"],
        "Top ingredient 1": ["tomato", "bread"],
        "Top ingredient 2": ["cheese", "butter"],
        "Top ingredient 3": ["basil", "sugar"],
        "Top ingredient 4": ["olive oil", "milk"],
        "Top ingredient 5": ["garlic", "flour"]
    })

    # Initialize the analyzer with sample data
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6],
        "cuisine": ["Italian", "American", "Mexican", "Greek", "Mexican", "Italian"],
        "ingredients": [
            "['tomato', 'cheese', 'basil', 'olive oil', 'garlic']",
            "['bread', 'butter', 'sugar', 'milk', 'flour']",
            "['tortilla', 'beans', 'chili powder', 'corn', 'cheese']",
            "['olive oil', 'feta', 'oregano', 'lemon', 'cucumber']",
            "['tortilla', 'chili powder', 'avocado', 'cheese', 'tomato']",
            "['tomato', 'cheese', 'garlic', 'basil', 'olive oil']"
        ]
    })
    analyzer = DataAnalyzer(data=sample_data)

    # Mock engine
    engine = MagicMock()

    # Test case 1: Data already exists in the database
    result = analyzer.top_commun_ingredients(engine)

    # Verify it returns the existing data
    mock_read_sql_table.assert_called_once_with("cuisine_top_ingredients", con=engine)
    pd.testing.assert_frame_equal(result, mock_read_sql_table.return_value)
    mock_to_sql.assert_not_called()

    # Test case 2: Data missing in the database
    mock_read_sql_table.side_effect = Exception("No table found")

    # Call the method to process the data
    result = analyzer.top_commun_ingredients(engine)

    # Expected processed DataFrame
    expected_result = pd.DataFrame({
        "cuisine": ["American", "Greek", "Italian", "Mexican"],
        "Top ingredient 1": ["bread", "olive oil", "tomato", "tortilla"],
        "Top ingredient 2": ["butter", "feta", "cheese", "chili powder"],
        "Top ingredient 3": ["sugar", "oregano", "basil", "cheese"],
        "Top ingredient 4": ["milk", "lemon", "olive oil", "beans"],
        "Top ingredient 5": ["flour", "cucumber", "garlic", "corn"]
    })

    # Ensure consistent dtype for textual columns
    text_columns = ["cuisine", "Top ingredient 1", "Top ingredient 2", "Top ingredient 3", "Top ingredient 4", "Top ingredient 5"]
    for col in text_columns:
        result[col] = result[col].astype("string")
        expected_result[col] = expected_result[col].astype("string")

    # Validate the result structure and content
    pd.testing.assert_frame_equal(
        result.sort_values("cuisine").reset_index(drop=True),
        expected_result.sort_values("cuisine").reset_index(drop=True)
    )

    # Ensure the result is saved to the database
    mock_to_sql.assert_called_once_with(
        name="cuisine_top_ingredients",
        con=engine,
        if_exists="replace"
    )

@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
@patch("projet_kbd.data_analyzer.utils.relevant_cuisines", ["Italian", "American", "Mexican", "Greek"])
def test_cuisine_evolution(mock_to_sql, mock_read_sql_table):
    """
    Test the `cuisine_evolution` method.

    This test ensures that the method correctly analyzes the evolution of
    different cuisines over the years and handles cases where data is already
    present in the database or needs to be calculated and saved.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.

    Assertions
    ----------
    - The method returns the existing data if found in the database.
    - The method calculates and returns the correct evolution of cuisines if
      no data is found in the database.
    - The method saves the calculated evolution of cuisines to the database.
    """
    # Simulate data already in the database
    mock_read_sql_table.return_value = pd.DataFrame({
        "Year": [2002, 2003],
        "American": [50.0, 40.0],
        "Greek": [5.0, 5.0],
        "Italian": [30.0, 35.0],
        "Greek": [15.0, 20.0]
    }).set_index("Year")

    # Initialize the analyzer with sample data
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6],
        "cuisine": ["Italian", "American", "Mexican", "Greek", "Mexican", "Italian"],
        "year": [2002, 2002, 2003, 2003, 2003, 2003]
    })
    analyzer = DataAnalyzer(data=sample_data)

    # Mock SQLAlchemy engine
    engine = MagicMock()

    # Test case 1: Data already exists in the database
    result = analyzer.cuisine_evolution(engine)

    # Validate it returns the existing database data
    mock_read_sql_table.assert_called_once_with("cuisine_evolution_dataframe", con=engine)
    pd.testing.assert_frame_equal(result, mock_read_sql_table.return_value)
    mock_to_sql.assert_not_called()

    # Test case 2: Data not found in the database
    mock_read_sql_table.side_effect = Exception("No table found")

    # Call the method to process the data
    result = analyzer.cuisine_evolution(engine)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)

    # Expected processed DataFrame
    expected_result = pd.DataFrame({
        "Cuisine": ["American", "Greek", "Italian", "Mexican"],
        2002: [50.0, 0.0, 50.0, 0.0],
        2003: [0.0, 25.0, 25.0, 50.0],
        2004: [0.0, 0.0, 0.0, 0.0],
        2005: [0.0, 0.0, 0.0, 0.0],
        2006: [0.0, 0.0, 0.0, 0.0],
        2007: [0.0, 0.0, 0.0, 0.0],
        2008: [0.0, 0.0, 0.0, 0.0],
        2009: [0.0, 0.0, 0.0, 0.0],
        2010: [0.0, 0.0, 0.0, 0.0]
    }).set_index("Cuisine").T

    expected_result = expected_result.reset_index().rename(columns={"index": "Year"}).set_index("Year")
    expected_result.columns.name = "Cuisine"

    # Updated validation
    pd.testing.assert_frame_equal(
        result,
        expected_result
    )

    # Ensure the result is saved to the database
    mock_to_sql.assert_called_once_with(
        name="cuisine_evolution_dataframe",
        con=engine,
        if_exists="replace",
        index=True,
        index_label="Year"
    )


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
@patch("projet_kbd.data_analyzer.utils.relevant_cuisines", ["Italian", "American", "Mexican", "Greek"])
def test_analyse_cuisine_nutritions(mock_to_sql, mock_read_sql_table):
    """
    Test the `analyse_cuisine_nutritions` method.

    This test ensures that the method correctly analyzes the nutritional
    information of different cuisines and handles cases where data is already
    present in the database or needs to be calculated and saved.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from the database.

    Assertions
    ----------
    - The method returns the existing data if found in the database.
    - The method calculates and returns the correct nutritional information if
      no data is found in the database.
    - The method saves the calculated nutritional information to the database.
    """
    # Simulate data already in the database
    mock_read_sql_table.return_value = pd.DataFrame({
        "cuisine": ["Italian", "American"],
        "sugar": [5.0, 4.5],
        "protein": [10.0, 8.5],
        "carbs": [40.0, 35.0],
        "totalFat": [20.0, 18.0],
        "satFat": [8.0, 6.0],
        "sodium": [500.0, 450.0],
        "cal": [300.0, 280.0],
        "minutes": [30.0, 25.0]
    })

    # Initialize the analyzer with sample data
    sample_data = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "cuisine": ["Italian", "American", "Mexican", "Greek"],
        "sugar": [5.0, 4.5, 6.0, 3.0],
        "protein": [10.0, 8.5, 12.0, 9.0],
        "carbs": [40.0, 35.0, 50.0, 30.0],
        "totalFat": [20.0, 18.0, 25.0, 15.0],
        "satFat": [8.0, 6.0, 10.0, 4.0],
        "sodium": [500.0, 450.0, 600.0, 400.0],
        "cal": [300.0, 280.0, 350.0, 250.0],
        "minutes": [30.0, 25.0, 40.0, 20.0]
    })
    analyzer = DataAnalyzer(data=sample_data)

    # Mock engine
    engine = MagicMock()

    # Test case 1: Data already exists in the database
    result = analyzer.analyse_cuisine_nutritions(engine)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)

    # Validate it returns the existing database data
    mock_read_sql_table.assert_called_once_with("cuisines_nutritions", con=engine)
    pd.testing.assert_frame_equal(result, mock_read_sql_table.return_value)
    mock_to_sql.assert_not_called()

    # Test case 2: Data not found in the database
    mock_read_sql_table.side_effect = Exception("No table found")

    # Call the method to process the data
    result = analyzer.analyse_cuisine_nutritions(engine)

    # Expected processed DataFrame
    expected_result = pd.DataFrame({
        "sugar": [4.5, 3.0, 5.0, 6.0],
        "protein": [8.5, 9.0, 10.0, 12.0],
        "carbs": [35.0, 30.0, 40.0, 50.0],
        "totalFat": [18.0, 15.0, 20.0, 25.0],
        "satFat": [6.0, 4.0, 8.0, 10.0],
        "sodium": [450.0, 400.0, 500.0, 600.0],
        "cal": [280.0, 250.0, 300.0, 350.0],
        "minutes": [25.0, 20.0, 30.0, 40.0],
    }, index=["American", "Greek", "Italian", "Mexican"])

    expected_result.index.name = "cuisine"

    # Validate the result structure and content
    pd.testing.assert_frame_equal(
        result.sort_index(),
        expected_result.sort_index()
    )

    # Ensure the result is saved to the database
    mock_to_sql.assert_called_once_with(
        name="cuisines_nutritions",
        con=engine,
        if_exists="replace"
    )


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
def test_proportion_quick_recipe(
    mock_to_sql, mock_read_sql_table, sample_data, mock_engine
):
    """
    Test the `proportion_quick_recipe` function from the `data_analyzer`
    module.

    This test verifies the behavior of the `proportion_quick_recipe` function
    when:
    1. The database table is empty, forcing the function to calculate the
    proportions.
    2. The function processes the provided sample data to compute the expected
    output.
    3. The function saves the results correctly to the database.

    Steps tested:
    - Mocking database interactions (`read_sql_table` and `to_sql`).
    - Validating the structure of the output DataFrame.
    - Ensuring data is saved to the database with the correct parameters.

    Mocks:
    -------
    - `pd.read_sql_table`: Simulates an empty database table.
    - `pd.DataFrame.to_sql`: Verifies that the calculated results are saved to
    the database.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mocked version of `pd.DataFrame.to_sql` to intercept database write
        operations.
    mock_read_sql_table : MagicMock
        Mocked version of `pd.read_sql_table` to simulate reading from an
        empty database table.
    sample_data : pd.DataFrame (fixture)
        Sample data used for testing the function. Contains realistic test
        data.
    mock_engine : MagicMock (fixture)
        Mocked database engine used to simulate database connections.

    Returns
    -------
    None
        This test does not return any value but validates the function's
        behavior.

    Assertions
    ----------
    - Ensures the output DataFrame contains the expected columns: `Year` and
    `Proportion`.
    - Confirms that the function attempts to save the results to the database
    table
      `quick_recipe_proportion_table`.

    Raises
    ------
    AssertionError
        If the output structure or database interactions do not match the
        expected behavior.
    """
    # Simuler une base de données vide pour forcer le calcul
    mock_read_sql_table.return_value = pd.DataFrame()

    # Créer une instance avec des données fictives
    analyzer = DataAnalyzer(data=sample_data)

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
    relative to relevant recipes per year, correctly handles missing database
    data, and stores the results in the database.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from an empty
        database table.
    sample_data : pd.DataFrame
        Fixture containing realistic sample data for testing.
    mock_engine : MagicMock
        Mock database engine to simulate database connections.

    Assertions
    ----------
    - The resulting DataFrame matches the expected proportions for each year.
    - The function writes the results to the database table
    `quick_recipe_proportion_table`.
    """
    # Simulate an empty database table to force calculation
    mock_read_sql_table.return_value = pd.DataFrame()

    # Create a DataAnalyzer instance
    analyzer = DataAnalyzer(sample_data)

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

    This test ensures the function calculates the interaction rate for quick
    recipes
    relative to all interactions per year, handles missing database data,
    and stores the results in the database.

    Parameters
    ----------
    mock_to_sql : MagicMock
        Mock for `pd.DataFrame.to_sql` to intercept database write operations.
    mock_read_sql_table : MagicMock
        Mock for `pd.read_sql_table` to simulate reading from an empty
        database table.
    sample_data : pd.DataFrame
        Fixture containing realistic sample data for testing.
    mock_engine : MagicMock
        Mock database engine to simulate database connections.

    Assertions
    ----------
    - The resulting DataFrame matches the expected interaction rates for each
    year.
    - The function writes the results to the database table
    `rate_interactions_for_quick_recipe`.
    """
    # Simulate an empty database table to force calculation
    mock_read_sql_table.return_value = pd.DataFrame()

    # Create a DataAnalyzer instance
    analyzer = DataAnalyzer(sample_data)

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
    analyzer = DataAnalyzer(sample_data)

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


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
def test_analyse_interactions_ratings(
    mock_to_sql, mock_read_sql_table, sample_data, mock_engine
):
    """
    Test the `analyse_interactions_ratings` function.

    This test validates that the method aggregates interaction and rating data
    correctly and returns the expected results in a DataFrame.
    It also verifies expected behavior using mocked database operations.
    """

    # Simulate an empty database table, ensuring no pre-existing state issues
    mock_read_sql_table.return_value = pd.DataFrame()

    # Create a DataAnalyzer instance
    analyzer = DataAnalyzer(sample_data)

    # Call the function
    result = analyzer.analyse_interactions_ratings(mock_engine)

    # Expected values based on provided sample data logic
    expected = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6, 7],
            "avg_rating": [4.0, 5.0, 3.0, 4.5, 5.0, 2.0, 3.5],
            "num_ratings": [1, 1, 1, 1, 1, 1, 1],
            "mean_minutes": [30.0, 45.0, 15.0, 60.0, 20.0, 50.0, 25.0],
        }
    )

    # Compare the actual DataFrame against the expected values
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
def test_analyse_average_steps_rating(
    mock_to_sql, mock_read_sql_table, sample_data, mock_engine
):
    """
    Test the `analyse_average_steps_rating` function.
    This test validates that the method calculates the average
    steps and average ratingsper year based on the provided sample data.
    """
    # Simulate an empty database table
    mock_read_sql_table.return_value = pd.DataFrame()

    # Create the DataAnalyzer instance
    analyzer = DataAnalyzer(sample_data)

    # Call the method
    result = analyzer.analyse_average_steps_rating(mock_engine)

    # Expected data based on the sample data
    expected = pd.DataFrame({
        "year": [2020, 2021, 2022, 2023],
        "avg_steps": [1100.0, 900.0, 1200.0, 1100.0],
        "avg_rating": [4.50, 3.75, 3.50, 3.50]
    }).astype({
        "year": "int32",
        "avg_steps": "float64",
        "avg_rating": "float64"
    })

    # Compare the actual DataFrame to expected values
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


@patch("projet_kbd.data_analyzer.pd.read_sql_table")
@patch("projet_kbd.data_analyzer.pd.DataFrame.to_sql")
def test_analyse_user_interactions(
    mock_to_sql, mock_read_sql_table, sample_data, mock_engine
):
    """
    Test the `analyse_user_intractions` function.
    This test validates that the method calculates interactions
    and average ratings grouped by days since submission correctly.
    """
    # Simulate database state with empty initial read
    mock_read_sql_table.return_value = pd.DataFrame()

    # Create the DataAnalyzer instance with the sample data
    analyzer = DataAnalyzer(sample_data)

    # Call the method
    result = analyzer.analyse_user_intractions(mock_engine)

    # Expected result calculation
    expected = pd.DataFrame(
        {
            "days_since_submission": [2, 5, 40],
            "num_interactions": [1, 5, 1],
            "avg_rating": [4.5, 4.1, 2.0]
        }
    )

    # Assert that the DataFrame matches expected results
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)
