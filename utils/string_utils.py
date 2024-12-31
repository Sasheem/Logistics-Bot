# utils/string_utils.py

import re

def normalize_string(s):
    if not isinstance(s, str):
        return ''
    return re.sub(r'\W+', '', s).lower()