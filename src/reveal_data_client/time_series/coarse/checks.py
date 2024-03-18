"""
This module defines various format and completeness checks for the coarse time series of the Reveal
dataset.
"""

import logging
from typing import Sequence

import pandas as pd

from reveal_data_client.constants import AnsPeriod, VnsStatus
from reveal_data_client.time_series.coarse.constants import CsvColumn

LOG = logging.getLogger(__name__)

EXPECTED_SAMPLING_RATE = 250  # Hz

EXPECTED_ANS_PERIODS_AND_VNS_STATUS = {
    (AnsPeriod.STIM1, VnsStatus.ON),
    (AnsPeriod.STIM2, VnsStatus.ON),
    (AnsPeriod.STIM3, VnsStatus.ON),
    (AnsPeriod.REST, VnsStatus.OFF),
    (AnsPeriod.IHG, VnsStatus.ON),
    (AnsPeriod.IHG, VnsStatus.OFF),
    (AnsPeriod.PECO, VnsStatus.ON),
    (AnsPeriod.PECO, VnsStatus.OFF),
    (AnsPeriod.HUT, VnsStatus.ON),
    (AnsPeriod.HUT, VnsStatus.OFF),
    (AnsPeriod.BASELINE_IHG, VnsStatus.OFF),
    (AnsPeriod.BASELINE_IHG, VnsStatus.ON),
    (AnsPeriod.RECOVERY_PECO, VnsStatus.OFF),
    (AnsPeriod.RECOVERY_PECO, VnsStatus.ON),
    (AnsPeriod.BASELINE_HUT, VnsStatus.OFF),
    (AnsPeriod.RECOVERY_HUT, VnsStatus.ON),
}


def check_all_expected_ans_periods_and_vns_status_present(
    periods_and_vns_status: Sequence[tuple[AnsPeriod, VnsStatus]]
) -> None:
    """
    Check that all expected ANS periods and VNS status combinations are present in the data. Log a
    warning if any of the expected combinations are missing.

    :param periods_and_vns_status: The ANS periods and VNS status present in the data.
    """
    expected_periods_and_vns_status = set(EXPECTED_ANS_PERIODS_AND_VNS_STATUS)
    actual_periods_and_vns_status = set(periods_and_vns_status)
    if expected_periods_and_vns_status != actual_periods_and_vns_status:
        missing_values = expected_periods_and_vns_status - actual_periods_and_vns_status
        unexpected_values = actual_periods_and_vns_status - expected_periods_and_vns_status
        if missing_values:
            LOG.warning(
                "Missing ANS periods and VNS status in the data. Missing: %s",
                missing_values,
            )
        if unexpected_values:
            LOG.warning(
                "Unexpected ANS periods and VNS status in the data. Unexpected: %s",
                unexpected_values,
            )


def check_all_recording_channels_present(data: pd.DataFrame) -> None:
    """
    Check that all expected recording channels are present in the data. Log a warning if any of the
    expected channels are missing.

    :param data: The coarse time series data for a participant, visit, and ANS period.
    """

    # We expect all columns except the lab chart time (which is the index)
    expected_channels = set(column.value for column in CsvColumn) - {CsvColumn.LAB_CHART_TIME}
    actual_channels = set(data.columns)
    if expected_channels != actual_channels:
        missing_channels = expected_channels - actual_channels
        unexpected_channels = actual_channels - expected_channels
        if missing_channels:
            LOG.warning("Missing channels in the data. Missing: %s", missing_channels)
        if unexpected_channels:
            LOG.warning("Unexpected channels in the data. Unexpected: %s", unexpected_channels)


def check_sampling_rate(
    data: pd.DataFrame, expected_sampling_rate_hz: int = EXPECTED_SAMPLING_RATE
) -> None:
    """
    Check that the sampling rate of the data is as expected. Log a warning if the sampling rate is
    not as expected.

    :param data: The coarse time series data for a participant, visit, and ANS period.
    """
    elapsed = data.index[-1] - data.index[0]
    actual_sampling_rate = round(len(data) / elapsed.total_seconds())
    if actual_sampling_rate != expected_sampling_rate_hz:
        LOG.warning(
            "Unexpected sampling rate. Expected: %s, Actual: %s",
            expected_sampling_rate_hz,
            actual_sampling_rate,
        )
