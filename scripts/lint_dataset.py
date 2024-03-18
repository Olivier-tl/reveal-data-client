"""This module contains checks for the completness and format of the reveal dataset."""

import argparse
from pathlib import Path

import pandas as pd

from reveal_data_client import RevealDataClient
from reveal_data_client.constants import AnsPeriod, VisitID
from reveal_data_client.time_series.coarse.checks import (
    check_all_expected_ans_periods_and_vns_status_present,
    check_all_recording_channels_present,
    check_sampling_rate,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Load and plot coarse time-series data from the Reveal dataset."
    )
    parser.add_argument(
        "dataset_path",
        type=Path,
        help="Path to the root directory of the Reveal dataset.",
    )
    return parser.parse_args()


def lint_coarse_time_series(client: RevealDataClient) -> None:
    """Lints the coarse time series for completeness and format."""

    for participant_id in client.get_participant_ids():
        for visit_id in client.get_visit_ids(participant_id):
            ans_periods_and_vns_status = client.get_ans_periods_and_vns_status(
                participant_id, visit_id
            )
            check_all_expected_ans_periods_and_vns_status_present(ans_periods_and_vns_status)
            for ans_period, vns_status in ans_periods_and_vns_status:
                coarse_time_series = client.coarse_time_series.get_data_for_ans_period(
                    participant_id, visit_id, ans_period, vns_status
                )
                check_all_recording_channels_present(coarse_time_series)
                check_sampling_rate(coarse_time_series)


def lint_dataset(dataset_path: Path) -> None:
    """
    We lint the dataset for data completeness and format. We check the following:

        1. We we have all expected recorded channels (BP, HR etc.)
        2. Do we have all expected ANS periods (stim1, stim2, stim3, rest, excercises... etc.)
        3. Is the sampling rate as expected?

    We log any issues we find.
    """
    client = RevealDataClient.from_path(dataset_path)

    print("Client created")

    lint_coarse_time_series(client)
    # TODO: Add checks for the other data sources


if __name__ == "__main__":
    args = parse_args()
    lint_dataset(args.dataset_path)
