"""
This module defines various format and completeness checks for the coarse time series of the Reveal
dataset.
"""

import logging
from typing import Sequence

import pandas as pd

from reveal_data_client import RevealDataClient
from reveal_data_client.constants import AnsPeriod, VnsStatus
from reveal_data_client.time_series.coarse.constants import CsvColumn
from reveal_data_client.validation import CheckResult

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


def check_missing_ans_periods_and_vns_status(
    periods_and_vns_status: Sequence[tuple[AnsPeriod, VnsStatus]]
) -> CheckResult:
    """
    Check that all expected ANS periods and VNS status combinations are present in the data.

    :param periods_and_vns_status: The ANS periods and VNS status present in the data.
    """
    expected_periods_and_vns_status = set(EXPECTED_ANS_PERIODS_AND_VNS_STATUS)
    actual_periods_and_vns_status = set(periods_and_vns_status)
    missing_values = expected_periods_and_vns_status - actual_periods_and_vns_status
    if missing_values:
        return CheckResult(
            name=check_missing_ans_periods_and_vns_status.__name__,
            passed=False,
            details=f"Missing ANS periods and VNS status in the data. Missing: {missing_values}",
        )
    return CheckResult(
        name=check_missing_ans_periods_and_vns_status.__name__,
        passed=True,
    )


def check_unexpected_ans_periods_and_vns_status(
    periods_and_vns_status: Sequence[tuple[AnsPeriod, VnsStatus]]
) -> CheckResult:
    """
    Check that no unexpected ANS periods and VNS status combinations are present in the data.

    :param periods_and_vns_status: The ANS periods and VNS status present in the data.
    """
    expected_periods_and_vns_status = set(EXPECTED_ANS_PERIODS_AND_VNS_STATUS)
    actual_periods_and_vns_status = set(periods_and_vns_status)
    unexpected_values = actual_periods_and_vns_status - expected_periods_and_vns_status
    if unexpected_values:
        return CheckResult(
            name=check_unexpected_ans_periods_and_vns_status.__name__,
            passed=False,
            details=(
                "Unexpected ANS periods and VNS status in the data. Unexpected: "
                f"{unexpected_values}"
            ),
        )
    return CheckResult(
        name=check_unexpected_ans_periods_and_vns_status.__name__,
        passed=True,
    )


def check_missing_recording_channels(data: pd.DataFrame) -> CheckResult:
    """
    Check that all expected recording channels are present in the data.

    :param data: The coarse time series data for a participant, visit, and ANS period.
    """
    expected_channels = set(CsvColumn.required())
    actual_channels = set(data.columns)
    missing_channels = expected_channels - actual_channels
    if missing_channels:
        return CheckResult(
            name=check_missing_recording_channels.__name__,
            passed=False,
            details=f"Missing channels in the data. Missing: {missing_channels}",
        )
    return CheckResult(
        name=check_missing_recording_channels.__name__,
        passed=True,
    )


def check_unexpected_recording_channels(data: pd.DataFrame) -> CheckResult:
    """
    Check that no unexpected recording channels are present in the data.

    :param data: The coarse time series data for a participant, visit, and ANS period.
    """
    expected_channels = set(CsvColumn.required())
    actual_channels = set(data.columns)
    unexpected_channels = actual_channels - expected_channels
    if unexpected_channels:
        return CheckResult(
            name=check_unexpected_recording_channels.__name__,
            passed=False,
            details=f"Unexpected channels in the data. Unexpected: {unexpected_channels}",
        )
    return CheckResult(
        name=check_unexpected_recording_channels.__name__,
        passed=True,
    )


def check_sampling_rate(
    data: pd.DataFrame, expected_sampling_rate_hz: int = EXPECTED_SAMPLING_RATE
) -> CheckResult:
    """
    Check that the sampling rate of the data is as expected. Log a warning if the sampling rate is
    not as expected.

    :param data: The coarse time series data for a participant, visit, and ANS period.
    :param expected_sampling_rate_hz: The expected sampling rate in Hz.
    """
    elapsed = data.index[-1] - data.index[0]
    actual_sampling_rate = round(len(data) / elapsed.total_seconds())
    if actual_sampling_rate != expected_sampling_rate_hz:
        return CheckResult(
            name=check_sampling_rate.__name__,
            passed=False,
            details=(
                f"Unexpected sampling rate. Expected: {expected_sampling_rate_hz}, Actual: "
                f"{actual_sampling_rate}"
            ),
        )
    return CheckResult(
        name=check_sampling_rate.__name__,
        passed=True,
    )


def validate_coarse_time_series(client: RevealDataClient) -> Sequence[CheckResult]:
    """Validates the coarse time series for completeness and format."""

    results = []
    for participant_id in client.get_participant_ids():
        for visit_id in client.get_visit_ids(participant_id):
            ans_periods_and_vns_status = client.get_ans_periods_and_vns_status(
                participant_id, visit_id
            )
            results.append(check_missing_ans_periods_and_vns_status(ans_periods_and_vns_status))
            results.append(check_unexpected_ans_periods_and_vns_status(ans_periods_and_vns_status))
            for ans_period, vns_status in ans_periods_and_vns_status:
                coarse_time_series = client.coarse_time_series.get_data_for_ans_period(
                    participant_id, visit_id, ans_period, vns_status
                )
                results.append(check_missing_recording_channels(coarse_time_series))
                results.append(check_unexpected_recording_channels(coarse_time_series))
                results.append(check_sampling_rate(coarse_time_series))
    return results
