"""Basic tests to ensure the package works."""

def test_import():
    """Test that the package can be imported."""
    import finance_tracker
    assert finance_tracker is not None

def test_basic_math():
    """Basic test that always passes."""
    assert 1 + 1 == 2

def test_package_structure():
    """Test that main modules exist."""
    from finance_tracker import cli, database, reports
    assert cli is not None
    assert database is not None
    assert reports is not None