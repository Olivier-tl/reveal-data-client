"""
This module contains classes and functions related to validation checks for the Reveal dataset.
"""

from dataclasses import dataclass


@dataclass
class CheckResult:
    """The result of a validation check."""

    name: str
    """The name of the validation check."""

    passed: bool
    """Whether the validation check passed."""

    details: str | None = None
    """If the validation check failed, a message describing the failure."""
