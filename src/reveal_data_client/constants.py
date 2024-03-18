"""This module contains the constants used in the Reveal dataset."""

from enum import Enum


class AnsPeriod(str, Enum):
    """
    Enum to represent the possible values for the ANS Period.
    For more information, see the raw data dictionary.
    """

    REST = "REST"

    STIM1 = "STIM1"
    """First acute stim of the day."""

    STIM2 = "STIM2"
    """Second acute stim of the day."""

    STIM3 = "STIM3"
    """Third acute stim of the day."""

    IHG = "IHG"
    """IHG_w/VNS on or off"""

    PECO = "PECO"
    """PECO_w/VNS on or off"""

    HUT = "HUT"
    """HUT w/ VNS on or off"""

    BASEIHG = "BASEIHG"

    RECPECO = "RECPECO"

    BASEHUT = "BASEHUT"

    RECHUT = "RECHUT"


class VisitID(str, Enum):
    """
    Enum to represent the possible values for the Visit ID.
    """

    SV1 = "SV1"
    """Visit 1"""

    SV2 = "SV2"
    """Visit 2"""
