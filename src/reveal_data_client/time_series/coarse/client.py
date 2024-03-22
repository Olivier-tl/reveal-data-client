"""This modules implements the `TimeSeriesClient` interface for the coarse time series data."""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Sequence

import pandas as pd

from reveal_data_client.constants import AnsPeriod, VisitID, VnsStatus
from reveal_data_client.time_series.api import TimeSeriesClient
from reveal_data_client.time_series.coarse.constants import CsvColumn
from reveal_data_client.time_series.coarse.utils import extract_participant_id

PRIMARY_DIR = Path("primary")
ANS_DIR = Path("ANS")
BY_PERIOD_DIR = Path("By Period")
PARTICIPANT_DIR_STR = "sub-{participant_id}"
FILENAME_STR = "{participant_id}_lab_ans_all.csv"
MAX_CACHE_SIZE = 20  # Maximum number of items to cache in the LRU cache (~200MB per file => 4GB)
LOG = logging.getLogger(__name__)


class CoarseTimeSeriesClient(TimeSeriesClient):
    """
    Client to access the coarse time series data. The coarse time series data is sampled at 250Hz.
    """

    def __init__(self, dataset_path: Path) -> None:
        """
        Create a new instance of the CoarseTimeSeriesClient.

        :param dataset_path: The path to the root directory of the dataset.
        """
        self._participants_path = dataset_path / PRIMARY_DIR

    def get_participant_ids(self) -> Sequence[str]:
        participant_folders = [f for f in self._participants_path.iterdir() if f.is_dir()]
        ids = []
        for participant_folder in participant_folders:
            try:
                participant_id = extract_participant_id(participant_folder.name)
                ids.append(participant_id)
            except ValueError:
                LOG.warning(
                    "Participant folder %s does not have a valid name, skipping.",
                    participant_folder,
                )
        return ids

    def get_visit_ids(self, participant_id: str) -> Sequence[VisitID]:
        # TODO: Get the visit IDs from the files in the "By Period" folder once available.
        #      For now, load the visit IDs from the data file.
        data = self._load_data(participant_id)

        return [VisitID(id) for id in data[CsvColumn.VISIT_ID].unique()]

    def get_ans_periods_and_vns_status(
        self, participant_id: str, visit_id: VisitID
    ) -> Sequence[tuple[AnsPeriod, VnsStatus]]:
        """Gets unique pairs of ANS periods and VNS status for a participant and visit."""
        data = self._load_data(participant_id)
        data = data[data[CsvColumn.VISIT_ID] == visit_id]
        return [
            (AnsPeriod(ans_period), VnsStatus(vns_status))
            for ans_period, vns_status in set(
                zip(data[CsvColumn.ANS_PERIOD], data[CsvColumn.ANS_STATUS])
            )
        ]

    def get_data_for_ans_period(
        self, participant_id: str, visit_id: VisitID, ans_period: AnsPeriod, vns_status: VnsStatus
    ) -> pd.DataFrame:
        data = self._load_data(participant_id)
        return data[
            (data[CsvColumn.PARTICIPANT_ID] == participant_id)
            & (data[CsvColumn.VISIT_ID] == visit_id)
            & (data[CsvColumn.ANS_PERIOD] == ans_period)
            & (data[CsvColumn.ANS_STATUS] == vns_status)
        ]

    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def _load_data(self, participant_id: str) -> pd.DataFrame:

        file_path = (
            self._participants_path
            / PARTICIPANT_DIR_STR.format(participant_id=participant_id)
            / ANS_DIR
            / FILENAME_STR.format(participant_id=participant_id)
        )

        # FIXME: This loads the entire dataset into memory. For large datasets,
        # we should use a more memory-efficient approach. The current sample file
        # is 200MB, which is fine, but we should validate that the full dataset
        # is not too large to fit into memory.
        df = pd.read_csv(file_path, delimiter="|")

        # Convert the time in seconds to a timedelta and set it as the index
        df[CsvColumn.index_col()] = pd.to_timedelta(df[CsvColumn.index_col()], unit="s")
        df.set_index(CsvColumn.index_col(), inplace=True)

        return df
