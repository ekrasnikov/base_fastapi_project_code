from unittest import mock

from data.hello.datasources.mock_db_hello import MockHelloDatasource

# from tests.utility import make_object, resolved_value


# def test_db_example():
# item = {'key1': 'value1', 'key2': 'value2'}
# datasource = SomeDatasource(
#     pg=make_object({'fetch': resolved_value([item])}),
#     logger=mock.Mock(),
# )
# result = await datasource.some_method()
# assert result == item


def test_hello():
    mock_db = MockHelloDatasource(logger=mock.Mock())

    assert mock_db.hello() == "Hello! This is base code"
