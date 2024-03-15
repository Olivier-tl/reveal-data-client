"""Interface to load and access time series data from the Reveal dataset."""

from abc import ABC


class TimeSeriesClient(ABC):
    ...
    # TODO: Extract a common interface for the `OriginalTimeSeriesClient` and the
    #       `CoarseTimeSeriesClient` here.
