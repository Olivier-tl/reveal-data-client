"""This modules implements the `TimeSeriesClient` interface for the coarse time series data."""

import logging
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Sequence

import pandas as pd

from reveal_data_client.constants import AnsPeriod, VisitID
from reveal_data_client.time_series.api import TimeSeriesClient

PRIMARY_DIR = Path("primary")
PARTICIPANT_DIR_STR = "sub-{participant_id}"
FILENAME_STR = "{participant_id}_{visit_id}_all.csv"
MAX_CACHE_SIZE = 20  # Maximum number of items to cache in the LRU cache (~200MB per file => 4GB)
LOG = logging.getLogger(__name__)


class CsvColumn(str, Enum):
    """
    Enum to represent the columns in the CSV file.
    """

    PARTICIPANT_ID = "Participant_ID"
    VISIT_ID = "Visit_ID"
    ANS_PERIOD = "ANS_Period"
    ANS_STATUS = "ANS_Status"
    LAB_CHART_TIME = "LabChartTime"
    ECG = "ECG"
    NIBP = "NIBP"
    HANDGRIP = "Handgrip"
    RESPIRATORY_WAVEFORM = "Respiratory_Waveform"
    SYSTOLIC = "Systolic"
    DIASTOLIC = "Diastolic"
    MEAN = "Mean"
    HEART_RATE = "HR"
    RAW_MSNA = "Raw MSNA"
    FILTERED_MSNA = "Filtered_MSNA"
    RMS_MSNA = "RMS_MSNA"
    RESPIRATORY_RATE = "Respiratory Rate"
    PERCENT_MVC = "%MVC"
    STIMULATOR = "Stimulator"
    INTEGRATED_MSNA = "Integrated_MSNA"
    COMMENT = "Comment"


class CoarseTimeSeriesClient(TimeSeriesClient):
    """
    Client to access the coarse time series data. The coarse time series data is sampled at 250Hz.
    """

    def __init__(self, dataset_path: Path) -> None:
        """
        Create a new instance of the CoarseTimeSeriesClient.

        :param dataset_path: The path to the root directory of the dataset.
        """
        self._dataset_path = dataset_path
        self._participants_path = dataset_path / PRIMARY_DIR

    def get_participant_ids(self) -> Sequence[str]:
        participant_folders = [f for f in self._participants_path.iterdir() if f.is_dir()]
        ids = []
        for participant_folder in participant_folders:
            try:
                participant_id = participant_folder.name.split("-")[1]
                ids.append(participant_id)
            except IndexError:
                LOG.warning(
                    "Participant folder %s does not have a valid name, skipping.",
                    participant_folder,
                )
        return ids

    def get_visit_ids(self, participant_id: str) -> Sequence[VisitID]:
        participant_folder = self._participants_path / PARTICIPANT_DIR_STR.format(
            participant_id=participant_id
        )
        participant_files = [f for f in participant_folder.iterdir() if f.is_file()]
        ids = []
        for f in participant_files:
            if f.suffix != ".csv":
                continue
            try:
                visit_id = f.name.split("_")[1]
                ids.append(VisitID(visit_id.upper()))
            except IndexError:
                LOG.warning("Participant file %s does not have a valid name, skipping.", f)
        return ids

    def get_ans_periods(self, participant_id: str, visit_id: VisitID) -> Sequence[AnsPeriod]:
        data = self._load_data(participant_id, visit_id)
        ans_periods_str = data[
            (data[CsvColumn.PARTICIPANT_ID] == participant_id)
            & (data[CsvColumn.VISIT_ID] == visit_id)
        ][CsvColumn.ANS_PERIOD].unique()
        return [AnsPeriod(period) for period in ans_periods_str]

    def get_data_for_ans_period(
        self, participant_id: str, visit_id: VisitID, ans_period: AnsPeriod, is_vns_on: bool
    ) -> pd.DataFrame:
        data = self._load_data(participant_id, visit_id)
        return data[
            (data[CsvColumn.PARTICIPANT_ID] == participant_id)
            & (data[CsvColumn.VISIT_ID] == visit_id)
            & (data[CsvColumn.ANS_PERIOD] == ans_period)
            & (data[CsvColumn.ANS_STATUS] == ("ON" if is_vns_on else "OFF"))
        ]

    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def _load_data(self, participant_id: str, visit_id: VisitID) -> pd.DataFrame:

        file_path = (
            self._participants_path
            / PARTICIPANT_DIR_STR.format(participant_id=participant_id)
            / FILENAME_STR.format(participant_id=participant_id, visit_id=visit_id.value.lower())
        )

        # FIXME: This loads the entire dataset into memory. For large datasets,
        # we should use a more memory-efficient approach. The current sample file
        # is 200MB, which is fine, but we should validate that the full dataset
        # is not too large to fit into memory.
        df = pd.read_csv(file_path)

        # Convert the time in seconds to a timedelta
        df[CsvColumn.LAB_CHART_TIME] = pd.to_timedelta(df[CsvColumn.LAB_CHART_TIME], unit="s")

        # Set the index to the time column
        df.set_index(CsvColumn.LAB_CHART_TIME, inplace=True)

        # Check the format of the data
        self._check_format(df, participant_id, visit_id)

        return df

    @staticmethod
    def _check_format(data: pd.DataFrame, participant_id: str, visit_id: VisitID) -> None:
        """
        Check the format of the data. Log a warning if the format is not as expected.
        """
        # Check that the columns are as expected
        expected_columns = set(column.value for column in CsvColumn) - {CsvColumn.LAB_CHART_TIME}
        actual_columns = set(data.columns)
        if expected_columns != actual_columns:
            LOG.warning(
                "Unexpected columns in the data. Expected: %s, Actual: %s",
                expected_columns,
                actual_columns,
            )

        # Check that the participant ID and visit ID are as expected. Only 1 participant and 1 visit
        # should be present in the data.
        actual_participant_ids = set(data[CsvColumn.PARTICIPANT_ID].unique())
        actual_visit_ids = set(data[CsvColumn.VISIT_ID].unique())
        if len(actual_participant_ids) != 1:
            LOG.warning("Expected 1 participant ID, found {%s}", len(actual_participant_ids))
        if len(actual_visit_ids) != 1:
            LOG.warning("Expected 1 visit ID, found {%s}", len(actual_visit_ids))
        if participant_id not in actual_participant_ids:
            LOG.warning("Participant ID {%s} not found in the data", participant_id)
        if visit_id.value not in actual_visit_ids:
            LOG.warning("Visit ID {%s} not found in the data", visit_id.value)

        # Check that the ANS period is as expected
        actual_ans_periods = set(data[CsvColumn.ANS_PERIOD].unique())
        expected_ans_periods = {period.value for period in AnsPeriod}
        if actual_ans_periods != expected_ans_periods:
            LOG.warning(
                "Unexpected ANS periods in the data. Expected: %s, Actual: %s",
                expected_ans_periods,
                actual_ans_periods,
            )
