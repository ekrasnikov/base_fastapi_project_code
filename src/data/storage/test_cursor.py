from data.storage.cursor import decode, encode


def test_decode():
    assert decode("eyJhYiI6MSwiY2QiOiJlZCJ9") == {"ab": 1, "cd": "ed"}


def test_encode():
    assert encode({"ab": 1, "cd": "ed"}) == "eyJhYiI6MSwiY2QiOiJlZCJ9"
