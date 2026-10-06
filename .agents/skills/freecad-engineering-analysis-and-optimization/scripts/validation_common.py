"""Shared validation primitives for engineering evidence contracts."""

import re


_SENTINEL = re.compile(
    r"(?:^|[\s<\[({:/_-])"
    r"(?:tbd|todo|unknown|unassigned|placeholder|replace[\s_-]?me|"
    r"to[\s_-]?be[\s_-]?determined|controlled[\s_-]?installed[\s_-]?version|"
    r"not[\s_-]?set|n/?a|none|null|yyyy[\s_-]?mm[\s_-]?dd|xxx|\?+)"
    r"(?:$|[\s>\])}:/_-])",
    re.IGNORECASE,
)


def is_sentinel(value):
    """Return True for common unresolved placeholder strings."""
    return isinstance(value, str) and bool(_SENTINEL.search(value.strip()))


def present(value):
    """Return True when a value exists and is not an unresolved placeholder."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and not is_sentinel(value)
    return True
