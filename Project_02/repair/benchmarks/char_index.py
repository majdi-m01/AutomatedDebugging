from typing import Optional

def char_index(s: str, c: str) -> Optional[int]:
    """Return the index in `s` where it matches `c`.
    Special character `*` matches any character.
    Return None if not matched."""
    for i in range(len(s)):
        x = s[i]
        if x == c: # fix here
            return i
        
    return None