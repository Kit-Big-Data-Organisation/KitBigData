from projet_kbd import utils


# Tests for the determine_cuisine function
def test_determine_cuisine():
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


# Tests for the highlight_cells function
def test_highlight_cells():
    assert (
        utils.highlight_cells("parmesan cheese") == "background-color: red"
    )
    assert (
        utils.highlight_cells("olive oil") == "background-color: lightgreen"
    )
    assert (
        utils.highlight_cells("chili powder") == "background-color: orange"
    )
    assert (
        utils.highlight_cells("flour tortillas") == "background-color: orange"
    )
    assert (
        utils.highlight_cells("feta cheese") == "background-color: lightblue"
    )
    assert (
        utils.highlight_cells("dried oregano") == "background-color: lightblue"
    )
    assert (
        utils.highlight_cells("soy sauce") == "background-color: lightpink"
    )
    # Test a value that should not highlight
    assert utils.highlight_cells("water") == ""
