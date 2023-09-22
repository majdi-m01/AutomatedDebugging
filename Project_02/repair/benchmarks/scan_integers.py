from typing import List

def scan_integers(seq: List[str]) -> List[int]:
    """Scan integer values from a `seq`. Stop when `-1` is read."""
    scanned = []
    for value in seq:
        try:                      # alternatively fix here
            int_value = int(value)
        except ValueError:
            continue
        
        scanned.append(int_value) # fix here

    return scanned
