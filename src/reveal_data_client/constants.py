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
    """Handgrip exercise with VNS ON or OFF"""

    PECO = "PECO"
    """Post-exercise circulatory occlusion with VNS ON or OFF"""

    HUT = "HUT"
    """Head-up tilt with VNS ON or OFF"""

    BASELINE_IHG = "BASEIHG"

    RECOVERY_PECO = "RECPECO"

    BASELINE_HUT = "BASEHUT"

    RECOVERY_HUT = "RECHUT"


class VisitID(str, Enum):
    """
    Enum to represent the possible values for the Visit ID.
    """

    SV1 = "SV1"
    """Visit 1"""

    SV2 = "SV2"
    """Visit 2"""


class VnsStatus(str, Enum):
    """
    Enum to represent the possible values for the VNS Status.
    """

    ON = "ON"
    """VNS is on"""

    OFF = "OFF"
    """VNS is off"""
