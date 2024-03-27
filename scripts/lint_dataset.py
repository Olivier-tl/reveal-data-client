"""This module contains checks for the completness and format of the reveal dataset."""

import logging
from pathlib import Path

import pandas as pd
from utils import parse_args

from reveal_data_client import RevealDataClient
from reveal_data_client.constants import AnsPeriod, VisitID
from reveal_data_client.time_series.coarse.checks import validate_coarse_time_series

LOG = logging.getLogger(__name__)


def lint_dataset(dataset_path: Path) -> None:
    """
    We lint the dataset for data completeness and format. We check the following:

        1. We we have all expected recorded channels (BP, HR etc.)
        2. Do we have all expected ANS periods (stim1, stim2, stim3, rest, excercises... etc.)
        3. Is the sampling rate as expected?

    We log any issues we find.
    """
    client = RevealDataClient.from_path(dataset_path)

    checks = validate_coarse_time_series(client)
    # TODO: Add checks for the other data sources

    successful_checks = [check for check in checks if check.passed]
    LOG.info(f"{len(successful_checks)}/{len(checks)} checks passed.")

    if len(successful_checks) == len(checks):
        LOG.info("All checks passed. 🌟")
    else:
        failed_checks = [check for check in checks if not check.passed]
        LOG.error(f"{len(failed_checks)}/{len(checks)} checks failed.")
        for check in failed_checks:
            LOG.error(check.details)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    lint_dataset(args.dataset_path)
