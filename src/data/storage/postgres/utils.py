import orjson


def json_encoder(*args, **kwargs):
    return orjson.dumps(*args, **kwargs).decode()
