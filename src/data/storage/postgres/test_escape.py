from data.storage.postgres.escape import escape_for_like


def test_escape_for_like():
    assert escape_for_like(r"%__\d") == r"\%\_\_\\d"
