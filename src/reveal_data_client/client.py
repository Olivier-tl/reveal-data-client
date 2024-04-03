"""Module implementing a client to access the Reveal dataset."""

from pathlib import Path
from typing import Sequence

from reveal_data_client.constants import AnsPeriod, VisitID, VnsStatus
from reveal_data_client.time_series.coarse.client import CoarseTimeSeriesClient
from reveal_data_client.types import ParticipantId

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

    def get_participant_ids(self) -> Sequence[ParticipantId]:
        """Get the participant IDs in the dataset."""
        # TODO: Refactor this in a separate MetadataClient class?
        return self._coarse_ts_client.get_participant_ids()

    def get_visit_ids(self, participant_id: ParticipantId) -> Sequence[VisitID]:
        """Get the visit IDs for a participant."""
        # TODO: Refactor this in a separate MetadataClient class?
        return self._coarse_ts_client.get_visit_ids(participant_id)

    def get_ans_periods_and_vns_status(
        self, participant_id: ParticipantId, visit_id: VisitID
    ) -> Sequence[tuple[AnsPeriod, VnsStatus]]:
        """Get the ANS periods and VNS status for a participant and visit."""
        # TODO: Refactor this in a separate MetadataClient class?
        return self._coarse_ts_client.get_ans_periods_and_vns_status(participant_id, visit_id)

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
