"""This module implements the `TimeSeriesClient` interface for the original time series data."""

from reveal_data_client.time_series.api import TimeSeriesClient


class OriginalTimeSeriesClient(TimeSeriesClient):
    """
    Client to access the raw sensor readings in an open format (e.g. EDF). At source sampling rate.
    """

    # TODO: Implement the `OriginalTimeSeriesClient` here once we agree on the data format.
