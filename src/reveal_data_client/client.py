"""Module implementing a client to access the Reveal dataset."""

from pathlib import Path
from typing import Sequence

from reveal_data_client.constants import AnsPeriod, VisitID
from reveal_data_client.time_series.coarse import CoarseTimeSeriesClient

PRIMARY_DIR = Path("primary")


class RevealDataClient:
    """
    Client to access the Reveal dataset. The client is a facade to access the different data
    sources in the Reveal dataset. This includes:
        - the original time series data,
        - the coarse time series data (250kHz),
        - the time series statistics (per minute),
        - stimulation response features (hr change, bp change, etc.),
    """

    # TODO: Swap the `CoarseTimeSeriesClient` with the `TimeSeriesClient` once we extract a
    #       common interface.
    def __init__(self, coarse_ts_client: CoarseTimeSeriesClient) -> None:
        """
        Create a new instance of the RevealDataClient.

        :param coarse_ts_client: The time series client to use to access the coarse time series
                                 data.
        """
        self._coarse_ts_client = coarse_ts_client

        # Initialize the participant IDs and the visit IDs
        # TODO: Check that the participant IDs and visit IDs are consistent across the different
        #       data sources.
        # TODO: Refactor this in a separate MetadataClient class?
        self._participant_ids = self._coarse_ts_client.get_participant_ids()
        self._participant_ids_to_visit_ids = {
            p_id: self._coarse_ts_client.get_visit_ids(p_id) for p_id in self._participant_ids
        }
        self._participant_ids_and_visit_ids_to_ans_periods = {
            p_id: {v_id: self._coarse_ts_client.get_ans_periods(p_id, v_id) for v_id in v_ids}
            for p_id, v_ids in self._participant_ids_to_visit_ids.items()
        }

    def get_participant_ids(self) -> Sequence[str]:
        """Get the participant IDs in the dataset."""
        return self._participant_ids

    def get_visit_ids(self, participant_id: str) -> Sequence[VisitID]:
        """Get the visit IDs for a participant."""
        return self._participant_ids_to_visit_ids[participant_id]

    def get_ans_periods(self, participant_id: str, visit_id: VisitID) -> Sequence[AnsPeriod]:
        """Get the ANS periods for a participant and visit."""
        return self._participant_ids_and_visit_ids_to_ans_periods[participant_id][visit_id]

    @property
    def coarse_time_series(self) -> CoarseTimeSeriesClient:
        """The time series client to use to access the coarse time series data."""
        return self._coarse_ts_client

    @staticmethod
    def from_path(dataset_path: Path) -> "RevealDataClient":
        """
        Create a new instance of the RevealDataClient from the path to the root directory of
        the dataset.

        :param dataset_path: The path to the root directory of the dataset.
        :return: A new instance of the RevealDataClient.
        """
        return RevealDataClient(coarse_ts_client=CoarseTimeSeriesClient(dataset_path))
