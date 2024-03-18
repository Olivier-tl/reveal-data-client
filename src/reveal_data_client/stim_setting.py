"""This module implements data loading of stimulation settings for the Reveal dataset."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Sequence

import pandas as pd

from reveal_data_client.constants import AnsPeriod

STIM_SETTING_FILE_PATH = "primary/stim_settings.csv"


class StimSettingCsvColumn(str, Enum):
    """
    Enum to represent the columns in the CSV file containing the stimulation settings.
    """

    STIM_OPTION = "stim_option"
    PULSE_WIDTH = "pulsewidth_ms"
    CURRENT = "level_ma"
    FREQUENCY = "freq_hz"
    DUTY_CYCLE_OFF = "duty_minoff"


@dataclass(frozen=True)
class StimSetting:
    """
    Data class to represent a stimulation setting.
    """

    stim_option: int
    """The stimulation option. A value between 1 and 6."""

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


def get_stim_settings(dataset_path: Path) -> Sequence[StimSetting]:
    """
    Get the stimulation settings from the CSV file.

    :param dataset_path: The path to the root directory of the dataset.
    :return: A sequence of stimulation settings.
    """
    stim_settings = pd.read_csv(dataset_path / STIM_SETTING_FILE_PATH)
    return [
        StimSetting(
            stim_option=row[StimSettingCsvColumn.STIM_OPTION],
            pulse_width=row[StimSettingCsvColumn.PULSE_WIDTH],
            current=row[StimSettingCsvColumn.CURRENT],
            frequency=row[StimSettingCsvColumn.FREQUENCY],
            duty_cycle_off=row[StimSettingCsvColumn.DUTY_CYCLE_OFF],
        )
        for _, row in stim_settings.iterrows()
    ]
