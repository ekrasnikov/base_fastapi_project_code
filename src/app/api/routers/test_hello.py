import datetime

import pytest
from freezegun import freeze_time
from utility.timestamp import timestamp

now = datetime.datetime.now()


@freeze_time()
@pytest.mark.functional
async def test_get_hello_info(di, client, logger):
    response = await client.get("/api/v1/hello/")
    assert response.status_code == 200
    print(
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    )
    result = response.json()
    assert result["message"] == "Hello! This is base code"
    assert result["timestamp"] == timestamp(now)
