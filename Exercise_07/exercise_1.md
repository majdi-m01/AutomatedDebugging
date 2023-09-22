# Exercise 7-1: No Silver Bullet
## _By Majdi Maalej_

This is the heartbeat example:
```sh
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
```

The Grammar type taken from the DebuggingBook chapter is as follows:
```sh
import string
from typing import Union, Any
Grammar = dict[str,  # A grammar maps strings...
               list[
                   Union[str,  # to list of strings...
                         tuple[str, dict[str, Any]]  # or to pairs of strings and attributes.
                        ]
               ]
              ]
```
A Grammar for the payload argument that can be of arbitrary length is created as follows:
```sh
PAYLOAD_GRAMMAR: Grammar = {
    "<start>": ["<payload>"],
    "<payload>": [
        "<char>",
        "<char><payload>",
    ],
    "<char>": list(string.ascii_letters + string.digits + string.punctuation)
}
```
Using the GrammarFuzzer introduced in the lecture, we generate a random input for the heartbeat function (Assuming length = 5) as follows: 
```sh
from fuzzingbook.GrammarFuzzer import GrammarFuzzer
payload_fuzzer = GrammarFuzzer(PAYLOAD_GRAMMAR)
while True:
    fuzz_input = payload_fuzzer.fuzz()
    try:
        heartbeat(length=5, payload=fuzz_input)
    except AssertionError:
        break
```
Printing out our random failure input of the payload:
```sh
print('failing_input=', fuzz_input)
```
_Output_
```sh
fuzz_input = +
```
The random failure input of the payload (fuzz_input) appeared randomly as '+'.

Now, coming to apply the DeltaDebugger from the debuggingbook on the random failure input found and printing out the minimal arguments that cause the function to fail (keeping the length as 5:
```sh
from debuggingbook.DeltaDebugger import DeltaDebugger
with DeltaDebugger() as dd:
    heartbeat(length=5, payload=fuzz_input)
print('minimized input:', dd.min_args())
```
_Output_
```sh
minimized input: {'length': 5, 'payload': ''}
```
With length of 5 as input, the minimum input of payload so that it fails is being a string with no content inside it. This makes sense, since that the first assertion statement checks if the legnth of the payload string is equal to the length input. Indeed, the minimum input of the payload would be of length zero, in order to fail the assertion statement.
However, this information is not enough to explain the failure reason, since it does not really show that the length of the payload matters.

Moving to apply DDSetDebugger on the random failure input found and getting the generalized pattern:
```sh
from debuggingbook.DDSetDebugger import DDSetDebugger
with DDSetDebugger(PAYLOAD_GRAMMAR) as dd_heartbeat:
    heartbeat(length=5, payload=fuzz_input)
print('Generalized Pattern:', dd_heartbeat)
```
_Output_
```sh
Generalized Pattern: heartbeat(length=5, payload='<start>')
```
With length of 5, this generalized pattern of payload creates most of the time a failure, except when the length of the payload is equal to the length variable. In other words, rarely is the generalized pattern correct.

In order to find the success rate of the generalized pattern, fuzz_args method of DDSetDebugger is invoked to produce 10,000 instantiations of the generalized pattern. Then, the number of failure inputs are calculated, and the rate is produced.
```sh
fails: int = 0
for i in range(10000):
    fuzzing = dd_heartbeat.fuzz_args()
    try:
        heartbeat(5, fuzzing.get('payload'))
    except AssertionError:
        fails += 1
print('success rate =', (10000-fails)*100/10000, '%')
```
_Output_
```sh
success rate = 2.9 %
```
As a result, the success rate of the generalized pattern is very low as expected.

A potential improvement for the informativity/expressiveness of the DDSetDebugger in order to become more helpful for the heartbeat case is by expanding the grammar of the input. In other words, the grammar should include all possible variations of both inputs 'length' as positive integer and 'payload' as a string of arbitrary length.
