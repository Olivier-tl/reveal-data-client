"""
This module contains the tests for the checks module in the coarse time series of the Reveal
dataset.
"""

import logging
from datetime import timedelta
from typing import List, Sequence

import pandas as pd
import pytest

from reveal_data_client.constants import AnsPeriod, VnsStatus
from reveal_data_client.time_series.coarse.checks import (
    EXPECTED_ANS_PERIODS_AND_VNS_STATUS,
    EXPECTED_SAMPLING_RATE,
    check_missing_ans_periods_and_vns_status,
    check_missing_recording_channels,
    check_sampling_rate,
    check_unexpected_ans_periods_and_vns_status,
    check_unexpected_recording_channels,
)
from reveal_data_client.time_series.coarse.constants import CsvColumn

UNEXPECTED_ANS_PERIOD_AND_VNS_STATUS = (AnsPeriod.STIM1, VnsStatus.OFF)


@pytest.mark.parametrize(
    "input, passed",
    [
        (list(EXPECTED_ANS_PERIODS_AND_VNS_STATUS), True),
        ([], False),
        (list(EXPECTED_ANS_PERIODS_AND_VNS_STATUS)[:-1], False),  # Missing one
    ],
)
def test_check_missing_ans_periods_and_vns_status(
    input: Sequence[tuple[AnsPeriod, VnsStatus]], passed: bool
) -> None:
    result = check_missing_ans_periods_and_vns_status(input)
    assert result.passed == passed


@pytest.mark.parametrize(
    "input, passed",
    [
        (list(EXPECTED_ANS_PERIODS_AND_VNS_STATUS), True),
        ([], True),  # No unexpected
        (
            list(EXPECTED_ANS_PERIODS_AND_VNS_STATUS) + [UNEXPECTED_ANS_PERIOD_AND_VNS_STATUS],
            False,
        ),  # Some unexpected
        ([UNEXPECTED_ANS_PERIOD_AND_VNS_STATUS], False),  # Only unexpected
    ],
)
def test_check_unexpected_ans_periods_and_vns_status(
    input: Sequence[tuple[AnsPeriod, VnsStatus]], passed: bool
) -> None:
    result = check_unexpected_ans_periods_and_vns_status(input)
    assert result.passed == passed


@pytest.mark.parametrize(
    "input, passed",
    [
        (CsvColumn.required(), True),  # All present
        ([], False),  # None present
        (CsvColumn.required()[:-1], False),  # Missing one
    ],
)
def test_check_missing_recording_channels(input: List[str], passed: bool) -> None:
    result = check_missing_recording_channels(pd.DataFrame(columns=input))
    assert result.passed == passed


@pytest.mark.parametrize(
    "input, passed",
    [
        (CsvColumn.required(), True),  # All present
        ([], True),  # None present
        (CsvColumn.required()[:-1], True),  # Missing one
        (CsvColumn.required() + ["unexpected"], False),  # Unexpected
        (["unexpected"], False),  # Only unexpected
    ],
)
def test_check_unexpected_recording_channels(input: list[str], passed: bool) -> None:
    result = check_unexpected_recording_channels(pd.DataFrame(columns=input))
    assert result.passed == passed


@pytest.mark.parametrize(
    "sampling_rate_hz, passed",
    [
        (EXPECTED_SAMPLING_RATE, True),
        (100, False),
    ],
)
def test_check_sampling_rate(sampling_rate_hz: int, passed: bool) -> None:
    expected_freq = timedelta(seconds=1 / sampling_rate_hz)
    idx = pd.date_range("1970-01-01", periods=1000, freq=expected_freq)
    data = pd.DataFrame(index=idx)
    result = check_sampling_rate(data)
    assert result.passed == passed
