"""This module collects constants used in `reveal_data_client.time_series.coarse`."""

from enum import Enum


class CsvColumn(Enum):
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

    @classmethod
    def required(cls) -> list[str]:
        return [col.value for col in cls if col != cls.LAB_CHART_TIME]

    @classmethod
    def index(cls) -> str:
        return cls.LAB_CHART_TIME.value
