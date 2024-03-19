"""
This module contains the tests for the checks module in the coarse time series of the Reveal
dataset.
"""

import logging
from datetime import timedelta

import pandas as pd

from reveal_data_client.constants import AnsPeriod, VnsStatus
from reveal_data_client.time_series.coarse.checks import (
    EXPECTED_ANS_PERIODS_AND_VNS_STATUS,
    EXPECTED_SAMPLING_RATE,
    check_all_expected_ans_periods_and_vns_status_present,
    check_all_recording_channels_present,
    check_sampling_rate,
)
from reveal_data_client.time_series.coarse.constants import CsvColumn

UNEXPECTED_SAMPLING_RATE = 100  # Hz
UNEXPECTED_ANS_PERIOD_AND_VNS_STATUS = (AnsPeriod.STIM1, VnsStatus.OFF)


def test_check_all_expected_ans_periods_and_vns_status_present_complete(caplog) -> None:
    with caplog.at_level(logging.WARNING):
        check_all_expected_ans_periods_and_vns_status_present(
            list(EXPECTED_ANS_PERIODS_AND_VNS_STATUS)
        )
    assert not caplog.records  # No warnings should be logged


def test_check_all_expected_ans_periods_and_vns_status_present_missing(caplog) -> None:
    ans_periods_and_vns_status_missing = list(EXPECTED_ANS_PERIODS_AND_VNS_STATUS)[:-1]
    with caplog.at_level(logging.WARNING):
        check_all_expected_ans_periods_and_vns_status_present(ans_periods_and_vns_status_missing)
    assert caplog.records  # Warnings should be logged


def test_check_all_expected_ans_periods_and_vns_status_present_unexpected(caplog) -> None:
    unexpected_ans_period_and_vns_status = list(EXPECTED_ANS_PERIODS_AND_VNS_STATUS) + [
        UNEXPECTED_ANS_PERIOD_AND_VNS_STATUS
    ]
    with caplog.at_level(logging.WARNING):
        check_all_expected_ans_periods_and_vns_status_present(unexpected_ans_period_and_vns_status)
    assert caplog.records  # Warnings should be logged


def test_check_all_recording_channels_present_complete(caplog) -> None:
    # Lab chart time is the index, so it is not included in the expected columns
    expected_columns = [col.value for col in CsvColumn if col != CsvColumn.LAB_CHART_TIME]
    data = pd.DataFrame(columns=expected_columns)
    with caplog.at_level(logging.WARNING):
        check_all_recording_channels_present(data)
    assert not caplog.records  # No warnings should be logged


def test_check_all_recording_channels_present_missing(caplog) -> None:
    data = pd.DataFrame(columns=[col.value for col in CsvColumn])
    data = data.drop(columns=[CsvColumn.HEART_RATE.value])  # Missing heart rate
    with caplog.at_level(logging.WARNING):
        check_all_recording_channels_present(data)
    assert caplog.records  # Warnings should be logged


# Test for check_sampling_rate
def test_check_sampling_rate_correct(caplog):
    expected_freq = timedelta(seconds=1 / EXPECTED_SAMPLING_RATE)
    idx = pd.date_range("2020-01-01", periods=1000, freq=expected_freq)
    data = pd.DataFrame(index=idx)
    with caplog.at_level(logging.WARNING):
        check_sampling_rate(data)
    assert not caplog.records  # No warnings should be logged


def test_check_sampling_rate_incorrect(caplog):
    expected_freq = timedelta(seconds=1 / UNEXPECTED_SAMPLING_RATE)
    idx = pd.date_range("2020-01-01", periods=100, freq=expected_freq)
    data = pd.DataFrame(index=idx)
    with caplog.at_level(logging.WARNING):
        check_sampling_rate(data)
    assert caplog.records  # Warnings should be logged
