from debuggingbook.DynamicInvariants import precondition, postcondition

data = 'password:hjasdiebk456jhaccount:smytzek'

@postcondition(lambda return_value, payload: data.startswith(payload))
def store_data(payload: str):
    global data
    data = payload + data

@precondition(lambda length: len(data)>= length)
@postcondition(lambda return_value, length: return_value == data[:length])
@postcondition(lambda return_value, length: length == len(return_value))
def get_data(length: int) -> str:
    return data[:min(length, len(data) + 1)]

def heartbeat(length: int, payload: str) -> str:
    store_data(payload)
    return get_data(length)