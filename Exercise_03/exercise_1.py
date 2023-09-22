data = 'password:hjasdiebk456jhaccount:smytzek'


def store_data(payload: str):
    global data
    data = payload + data


def get_data(length: int) -> str:
    return data[:min(length, len(data) + 1)]


def heartbeat(length: int, payload: str) -> str:
    assert isinstance(length, int)
    assert length > 0
    assert len(payload) >= length
    assert isinstance(payload, str)
    assert len(payload).bit_length() <= 16
    store_data(payload)
    assert payload in get_data(length)
    return get_data(length)
