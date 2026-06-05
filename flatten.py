"""Helper module for a simple speckle object tree flattening."""

from collections.abc import Iterable
from typing import Any


def flatten_base(base: Any) -> Iterable[Any]:
    """Flatten a base object into an iterable of nested objects.

    This function recursively traverses the `elements` or `@elements` attribute of the
    base object, yielding each nested object in the hierarchy.

    Args:
        base (Any): The base object to flatten.

    Yields:
        Any: Each nested object in the hierarchy.
    """
    elements = getattr(base, "elements", getattr(base, "@elements", None))

    if elements is not None:
        for element in elements:
            yield from flatten_base(element)

    yield base
