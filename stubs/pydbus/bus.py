"""
Stubs for pydbus.bus.

The stubs in this file do not necessarily match the structure of pydbus.
"""
from typing import Any

from .publication import Publication


class Bus:
    """Represents a DBus Bus."""

    def get(self, bus_name: str) -> Any: ...
    def publish(self, bus_name: str, *objects: Any) -> Publication: ...


def SystemBus() -> Bus:
    """Connect to the system bus."""
    ...


def SessionBus() -> Bus:
    """Connect to the session bus."""
    ...
