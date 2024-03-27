"""BP data model for the processed ambulatory blood pressure data."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np
import pandas as pd

HOURS_MINUTES_FORMAT = "%H:%M"
TIME_FORMAT = "%H:%M:%S"


def parse_time(time: str | float) -> datetime | None:
    """Parse a time string in the format HH:MM:SS.FFFFFFF. For example, 14:22:00.0000000."""
    if isinstance(time, float):
        if np.isnan(time):
            return None
        else:
            raise ValueError(f"Expected NaN, got {time}")
    # Discarding the fractional seconds, as they are always zero
    time = time.split(".")[0]  # Discard the fractional seconds
    return datetime.strptime(time, TIME_FORMAT)


def parse_hours_minutes(time: str) -> datetime:
    """Parse a time string in the format HH:MM. For example, 14:30."""
    return datetime.strptime(time, HOURS_MINUTES_FORMAT)


class ProcessedCSVColumn(str, Enum):
    """
    Enum to represent the columns in the processed ambulatory BP CSV file.

    For source of truth, see the "Ambulatory BP Processed" sheet under
    "docs/Pilot Data Dictionary <version>.xlsx" of the Reveal dataset.
    """

    PARTICIPANT_ID = "Participant_ID"
    """Study ID of participant"""

    VISIT_ID = "Visit_ID"
    """Associated study visit of data"""

    DEID_RECORDING_START = "DeId_RecordingStart"
    """Date of recording start - date of enrollment"""

    RECORDING_START_TIME = "RecordingStartTime"
    """Time from the RecordingRecordingStartDateTime"""

    DBP_MIN_24HRS = "DBP_MIN_24HRS"
    """Minimum diastolic blood pressure during hours 1-24"""

    DBP_MAX_24HRS = "DBP_MAX_24HRS"
    """Maximum diastolic blood pressure during hours 1-24"""

    DBP_AVG_24HRS = "DBP_AVG_24HRS"
    """Average diastolic blood pressure during hours 1-24"""

    SBP_MIN_24HRS = "SBP_MIN_24HRS"
    """Minimum systolic blood pressure during hours 1-24"""

    SBP_MAX_24HRS = "SBP_MAX_24HRS"
    """Maximum systolic blood pressure during hours 1-24"""

    SBP_AVG_24HRS = "SBP_AVG_24HRS"
    """Average systolic blood pressure during hours 1-24"""

    DBP_MIN_DAY = "DBP_MIN_DAY"
    """Minimum diastolic blood pressure during 0600 to 2400"""

    DBP_MAX_DAY = "DBP_MAX_DAY"
    """Maximum diastolic blood pressure during 0600 to 2400"""

    DBP_AVG_DAY = "DBP_AVG_DAY"
    """Average diastolic blood pressure during 0600 to 2400"""

    SBP_MIN_DAY = "SBP_MIN_DAY"
    """Minimum systolic blood pressure during 0600 to 2400"""

    SBP_MAX_DAY = "SBP_MAX_DAY"
    """Maximum systolic blood pressure during 0600 to 2400"""

    SBP_AVG_DAY = "SBP_AVG_DAY"
    """Average systolic blood pressure during 0600 to 2400"""

    DBP_MIN_NARDAY = "DBP_MIN_NARDAY"
    """Narrow daytime – minimum DBP between 0900 and 2100"""

    DBP_MAX_NARDAY = "DBP_MAX_NARDAY"
    """Narrow daytime – maximum DBP between 0900 and 2100"""

    DBP_AVG_NARDAY = "DBP_AVG_NARDAY"
    """Narrow daytime – average DBP between 0900 and 2100"""

    SBP_MIN_NARDAY = "SBP_MIN_NARDAY"
    """Narrow daytime – minimum SBP between 0900 and 2100"""

    SBP_MAX_NARDAY = "SBP_MAX_NARDAY"
    """Narrow daytime – maximum SBP between 0900 and 2100"""

    SBP_AVG_NARDAY = "SBP_AVG_NARDAY"
    """Narrow daytime – average SBP between 0900 and 2100"""

    DBP_MIN_NIGHT = "DBP_MIN_NIGHT"
    """Minimum diastolic blood pressure during 0000 to 0600"""

    DBP_MAX_NIGHT = "DBP_MAX_NIGHT"
    """Maximum diastolic blood pressure during 0000 to 0600"""

    DBP_AVG_NIGHT = "DBP_AVG_NIGHT"
    """Average diastolic blood pressure during 0000 to 0600"""

    DBP_MIN_NARNT = "DBP_MIN_NARNT"
    """Narrow nighttime – minimum DBP between 0100 and 0600"""

    DBP_MAX_NARNT = "DBP_MAX_NARNT"
    """Narrow nighttime – maximum DBP between 0100 and 0600"""

    DBP_AVG_NARNT = "DBP_AVG_NARNT"
    """Narrow nighttime – average DBP between 0100 and 0600"""

    SBP_MIN_NIGHT = "SBP_MIN_NIGHT"
    """Minimum systolic blood pressure during 0000 to 0600"""

    SBP_MAX_NIGHT = "SBP_MAX_NIGHT"
    """Maximum systolic blood pressure during 0000 to 0600"""

    SBP_AVG_NIGHT = "SBP_AVG_NIGHT"
    """Average systolic blood pressure during 0000 to 0600"""

    SBP_MIN_NARNT = "SBP_MIN_NARNT"
    """Narrow nighttime – minimum SBP between 0100 and 0600"""

    SBP_MAX_NARNT = "SBP_MAX_NARNT"
    """Narrow nighttime – maximum SBP between 0100 and 0600"""

    SBP_AVG_NARNT = "SBP_AVG_NARNT"
    """Narrow nighttime – average SBP between 0100 and 0600"""

    BEDTIME = "bedtime"
    """What time did you go to bed?"""

    AWAKE = "awake"
    """What time did you awaken in the morning?"""

    FIRST_NAP_START = "first_nap_start"
    """What time did the first nap begin?"""

    FIRST_NAP_END = "first_nap_end"
    """What time did the first nap end?"""

    FIRST_NAP_TOTAL = "first_nap_total"
    """Number of minutes for first nap"""

    SECOND_NAP_START = "second_nap_start"
    """What time did the second nap begin?"""

    SECOND_NAP_END = "second_nap_end"
    """What time did the second nap end?"""

    SECOND_NAP_TOTAL = "second_nap_total"
    """Number of minutes for second nap"""

    THIRD_NAP_START = "third_nap_start"
    """What time did the third nap begin?"""

    THIRD_NAP_END = "third_nap_end"
    """What time did the third nap end?"""

    THIRD_NAP_TOTAL = "third_nap_total"
    """Number of minutes for third nap"""

    BATHROOM = "bathroom"
    """While wearing the ABPM during sleep, how many times did you wake up to use the bathroom?"""

    OTHER_THAN_BATHROOM = "other_than_bathroom"
    """Other than using the bathroom, how many times did you wake up and get out of bed?"""

    SLEEP_COMPARED_TO_USUAL = "sleep_compared_to_usual"
    """While wearing the monitor, how did you sleep compared to usual?"""


@dataclass
class BPFeatures:
    """Data model for the processed ambulatory blood pressure data."""

    participant_id: str
    visit_id: str
    deid_recording_start: int
    recording_start_time: datetime

    dbp_min_24hrs: int
    dbp_max_24hrs: int
    dbp_avg_24hrs: int
    sbp_min_24hrs: int
    sbp_max_24hrs: int
    sbp_avg_24hrs: int

    dbp_min_day: int
    dbp_max_day: int
    dbp_avg_day: int
    dbp_min_narday: int
    dbp_max_narday: int
    dbp_avg_narday: int

    sbp_min_day: int
    sbp_max_day: int
    sbp_avg_day: int
    sbp_min_narday: int
    sbp_max_narday: int
    sbp_avg_narday: int

    dbp_min_night: int
    dbp_max_night: int
    dbp_avg_night: int
    dbp_min_narnt: int
    dbp_max_narnt: int
    dbp_avg_narnt: int

    sbp_min_night: int
    sbp_max_night: int
    sbp_avg_night: int
    sbp_min_narnt: int
    sbp_max_narnt: int
    sbp_avg_narnt: int

    bedtime: datetime
    awake: datetime
    first_nap_start: datetime | None
    first_nap_end: datetime | None
    first_nap_total: int
    second_nap_start: datetime | None
    second_nap_end: datetime | None
    second_nap_total: int
    third_nap_start: datetime | None
    third_nap_end: datetime | None
    third_nap_total: int

    bathroom: int
    other_than_bathroom: int
    sleep_compared_to_usual: int

    @classmethod
    def from_csv(cls, csv_file: str) -> "BPFeatures":
        df = pd.read_csv(csv_file, nrows=1, delimiter="|")
        return cls(
            participant_id=df[ProcessedCSVColumn.PARTICIPANT_ID][0],
            visit_id=df[ProcessedCSVColumn.VISIT_ID][0],
            deid_recording_start=df[ProcessedCSVColumn.DEID_RECORDING_START][0],
            recording_start_time=datetime.strptime(
                df[ProcessedCSVColumn.RECORDING_START_TIME][0], "%H:%M"
            ),
            dbp_min_24hrs=df[ProcessedCSVColumn.DBP_MIN_24HRS][0],
            dbp_max_24hrs=df[ProcessedCSVColumn.DBP_MAX_24HRS][0],
            dbp_avg_24hrs=df[ProcessedCSVColumn.DBP_AVG_24HRS][0],
            sbp_min_24hrs=df[ProcessedCSVColumn.SBP_MIN_24HRS][0],
            sbp_max_24hrs=df[ProcessedCSVColumn.SBP_MAX_24HRS][0],
            sbp_avg_24hrs=df[ProcessedCSVColumn.SBP_AVG_24HRS][0],
            dbp_min_day=df[ProcessedCSVColumn.DBP_MIN_DAY][0],
            dbp_max_day=df[ProcessedCSVColumn.DBP_MAX_DAY][0],
            dbp_avg_day=df[ProcessedCSVColumn.DBP_AVG_DAY][0],
            dbp_min_narday=df[ProcessedCSVColumn.DBP_MIN_NARDAY][0],
            dbp_max_narday=df[ProcessedCSVColumn.DBP_MAX_NARDAY][0],
            dbp_avg_narday=df[ProcessedCSVColumn.DBP_AVG_NARDAY][0],
            sbp_min_day=df[ProcessedCSVColumn.SBP_MIN_DAY][0],
            sbp_max_day=df[ProcessedCSVColumn.SBP_MAX_DAY][0],
            sbp_avg_day=df[ProcessedCSVColumn.SBP_AVG_DAY][0],
            sbp_min_narday=df[ProcessedCSVColumn.SBP_MIN_NARDAY][0],
            sbp_max_narday=df[ProcessedCSVColumn.SBP_MAX_NARDAY][0],
            sbp_avg_narday=df[ProcessedCSVColumn.SBP_AVG_NARDAY][0],
            dbp_min_night=df[ProcessedCSVColumn.DBP_MIN_NIGHT][0],
            dbp_max_night=df[ProcessedCSVColumn.DBP_MAX_NIGHT][0],
            dbp_avg_night=df[ProcessedCSVColumn.DBP_AVG_NIGHT][0],
            dbp_min_narnt=df[ProcessedCSVColumn.DBP_MIN_NARNT][0],
            dbp_max_narnt=df[ProcessedCSVColumn.DBP_MAX_NARNT][0],
            dbp_avg_narnt=df[ProcessedCSVColumn.DBP_AVG_NARNT][0],
            sbp_min_night=df[ProcessedCSVColumn.SBP_MIN_NIGHT][0],
            sbp_max_night=df[ProcessedCSVColumn.SBP_MAX_NIGHT][0],
            sbp_avg_night=df[ProcessedCSVColumn.SBP_AVG_NIGHT][0],
            sbp_min_narnt=df[ProcessedCSVColumn.SBP_MIN_NARNT][0],
            sbp_max_narnt=df[ProcessedCSVColumn.SBP_MAX_NARNT][0],
            sbp_avg_narnt=df[ProcessedCSVColumn.SBP_AVG_NARNT][0],
            bedtime=parse_hours_minutes(df[ProcessedCSVColumn.BEDTIME][0]),
            awake=parse_hours_minutes(df[ProcessedCSVColumn.AWAKE][0]),
            first_nap_start=parse_time(df[ProcessedCSVColumn.FIRST_NAP_START][0]),
            first_nap_end=parse_time(df[ProcessedCSVColumn.FIRST_NAP_END][0]),
            first_nap_total=df[ProcessedCSVColumn.FIRST_NAP_TOTAL][0],
            second_nap_start=parse_time(df[ProcessedCSVColumn.SECOND_NAP_START][0]),
            second_nap_end=parse_time(df[ProcessedCSVColumn.SECOND_NAP_END][0]),
            second_nap_total=df[ProcessedCSVColumn.SECOND_NAP_TOTAL][0],
            third_nap_start=parse_time(df[ProcessedCSVColumn.THIRD_NAP_START][0]),
            third_nap_end=parse_time(df[ProcessedCSVColumn.THIRD_NAP_END][0]),
            third_nap_total=df[ProcessedCSVColumn.THIRD_NAP_TOTAL][0],
            bathroom=df[ProcessedCSVColumn.BATHROOM][0],
            other_than_bathroom=df[ProcessedCSVColumn.OTHER_THAN_BATHROOM][0],
            sleep_compared_to_usual=df[ProcessedCSVColumn.SLEEP_COMPARED_TO_USUAL][0],
        )
