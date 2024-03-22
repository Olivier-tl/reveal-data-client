"""Utility functions for time series data."""

import re


def extract_participant_id(folder_name: str) -> str:
    """
    Extracts the participant ID from a folder name. e.g. sub-Sample-001 -> Sample-001

    :param folder_name: The folder name from which to extract the participant ID.
    :return: The extracted participant ID.
    :raises ValueError: If no ID is found.
    """
    match = re.search(r"sub-(\S+)", folder_name)
    if match:
        return match.group(1)
    else:
        raise ValueError("No ID found")
