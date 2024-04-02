"""This module implements data loading of stimulation settings for the Reveal dataset."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Mapping

import pandas as pd

from reveal_data_client.constants import AnsPeriod, VisitID

STIM_OPTION_MAPPING_FILE_PATH = "docs/rc_rand_vns_stim_parameters.csv"
PARTICIPANT_MAPPING_FILE_PATH = "docs/rc_rand_ans_participant_stim_settings.csv"


class StimOption(str, Enum):
    """
    Enum to represent the 6 different stimulation options.
    """

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


class StimOptionMappingCsvColumn(str, Enum):
    """
    Enum to represent the columns in the CSV file containing the stimulation settings.
    """

    STIM_OPTION = "stim_option"
    PULSE_WIDTH = "pulse_width_ms"
    CURRENT = "level_ma"
    FREQUENCY = "freq_hz"
    DUTY_CYCLE_OFF = "duty_cycle_off_min"


class ParticipantMappingCsvColumn(str, Enum):
    """
    Enum to represent the columns in the CSV file containing the participant mapping.
    """

    PARTICIPANT_ID = "Participant_ID"
    SV1_STIM1 = "SV1_STIM1"
    SV1_STIM2 = "SV1_STIM2"
    SV1_STIM3 = "SV1_STIM3"
    SV2_STIM1 = "SV2_STIM1"
    SV2_STIM2 = "SV2_STIM2"
    SV2_STIM3 = "SV2_STIM3"


@dataclass(frozen=True)
class StimSetting:
    """
    Data class to represent a stimulation setting.
    """

    pulse_width: float
    """The pulse width in milliseconds."""

    current: float
    """The current in mA."""

    frequency: int
    """The stimulation frequency in Hz."""

    duty_cycle_off: float
    """The duty cycle OFF time in minutes."""

    duty_cycle_on: float = 1.0
    """The duty cycle ON time in minutes. Default is 1.0 minutes."""


StimMapping = Dict[AnsPeriod, StimSetting]
"""A mapping from ANS period to stimulation settings."""


def get_ans_stim_mapping(
    dataset_path: Path,
) -> Mapping[tuple[str, VisitID, AnsPeriod], StimSetting]:
    """
    Gets the mapping from participant ID, visit ID, and ANS period to stimulation settings.

    :param dataset_path: The path to the root directory of the dataset.
    :return: A mapping from participant ID, visit ID, and ANS period to stimulation settings.
    """
    stim_option_mapping = _get_stim_option_mapping(dataset_path)
    participant_mapping = _get_participant_mapping(dataset_path)

    return {
        (participant_id, visit_id, ans_period): stim_option_mapping[stim_option]
        for (participant_id, visit_id, ans_period), stim_option in participant_mapping.items()
    }


def _get_stim_option_mapping(dataset_path: Path) -> Mapping[StimOption, StimSetting]:
    """
    Gets the mapping from stimulation option to stimulation settings.

    :param dataset_path: The path to the root directory of the dataset.
    :return: A mapping from stimulation option to stimulation settings.
    """
    stim_settings = pd.read_csv(dataset_path / STIM_OPTION_MAPPING_FILE_PATH, delimiter="|")
    return {
        StimOption(row[StimOptionMappingCsvColumn.STIM_OPTION]): StimSetting(
            pulse_width=row[StimOptionMappingCsvColumn.PULSE_WIDTH],
            current=row[StimOptionMappingCsvColumn.CURRENT],
            frequency=row[StimOptionMappingCsvColumn.FREQUENCY],
            duty_cycle_off=row[StimOptionMappingCsvColumn.DUTY_CYCLE_OFF],
        )
        for _, row in stim_settings.iterrows()
    }


def _get_participant_mapping(
    dataset_path: Path,
) -> Mapping[tuple[str, VisitID, AnsPeriod], StimOption]:
    """
    Gets the mapping from participant ID, visit ID, and ANS period to stim option.

    :param dataset_path: The path to the root directory of the dataset.
    :return: A mapping from participant ID, visit ID, and ANS period to stim option.
    """

    participant_mapping = pd.read_csv(dataset_path / PARTICIPANT_MAPPING_FILE_PATH, delimiter="|")

    mapping = {}

    col = ParticipantMappingCsvColumn
    for _, row in participant_mapping.iterrows():
        participant_id = row[col.PARTICIPANT_ID]
        mapping[(participant_id, VisitID.SV1, AnsPeriod.STIM1)] = StimOption(row[col.SV1_STIM1])
        mapping[(participant_id, VisitID.SV1, AnsPeriod.STIM2)] = StimOption(row[col.SV1_STIM2])
        mapping[(participant_id, VisitID.SV1, AnsPeriod.STIM3)] = StimOption(row[col.SV1_STIM3])
        mapping[(participant_id, VisitID.SV2, AnsPeriod.STIM1)] = StimOption(row[col.SV2_STIM1])
        mapping[(participant_id, VisitID.SV2, AnsPeriod.STIM2)] = StimOption(row[col.SV2_STIM2])
        mapping[(participant_id, VisitID.SV2, AnsPeriod.STIM3)] = StimOption(row[col.SV2_STIM3])

    return mapping
