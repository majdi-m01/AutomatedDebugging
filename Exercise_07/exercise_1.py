data = 'password:hjasdiebk456jhaccount:smytzek'
def store_data(payload: str):
    global data
    data = payload + data

def get_data(length: int) -> str:
    return data[:length]

def heartbeat(length: int, payload: str) -> str:
    assert length == len(payload)
    store_data(payload)
    assert data.startswith(payload)
    r = get_data(length)
    assert r == payload
    return r

import string
from typing import Union, Any
Grammar = dict[str,  # A grammar maps strings...
               list[
                   Union[str,  # to list of strings...
                         tuple[str, dict[str, Any]]  # or to pairs of strings and attributes.
                        ]
               ]
              ]
PAYLOAD_GRAMMAR: Grammar = {
    "<start>": ["<payload>"],
    "<payload>": [
        "<char>",
        "<char><payload>",
    ],
    "<char>": list(string.ascii_letters + string.digits + string.punctuation)
}

if __name__ == '__main__':
    from fuzzingbook.GrammarFuzzer import GrammarFuzzer
    payload_fuzzer = GrammarFuzzer(PAYLOAD_GRAMMAR)
    while True:
        fuzz_input = payload_fuzzer.fuzz()
        try:
            heartbeat(length=5, payload=fuzz_input)
        except AssertionError:
            break
    print('failing_input=', fuzz_input)

    from debuggingbook.DeltaDebugger import DeltaDebugger
    with DeltaDebugger() as dd:
        heartbeat(length=5, payload=fuzz_input)
    print('minimized input:', dd.min_args())

    from debuggingbook.DDSetDebugger import DDSetDebugger
    with DDSetDebugger(PAYLOAD_GRAMMAR) as dd_heartbeat:
        heartbeat(length=5, payload=fuzz_input)
    print('Generalized Pattern:', dd_heartbeat)

    fails: int = 0
    for i in range(10000):
        fuzzing = dd_heartbeat.fuzz_args()
        try:
            heartbeat(5, fuzzing.get('payload'))
        except AssertionError:
            fails += 1
    print('success rate =', (10000 - fails) * 100 / 10000, '%')