"""ECG data model for the processed ambulatory ECG data."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

import pandas as pd


class ProcessedCSVColumn(str, Enum):
    """Enum to represent the columns in the processed ambulatory ECG CSV file."""

    PARTICIPANT_ID = "Participant_ID"

    VISIT_ID = "Visit_ID"

    TOTAL_TIME = "tot_time"
    """Total monitored time in hours."""

    START_TIME = "start_time"
    """Time when monitoring began. Format: HH:MM:SS"""

    STOP_TIME = "stop_time"
    """Time when monitoring ended. Format: HH:MM:SS"""

    TOTAL_QRS = "total_QRS"
    """Total beats, Q-wave, R-wave, S-wave"""

    MAX_HR = "maxHR"
    """Overall maximum Heart rate"""

    MIN_HR = "minHR"
    """Overall minimum Heart rate"""

    AVG_HR = "avgHR"
    """Overall average Heart rate"""

    PVC_EVENTS = "PVC_events"
    """Ventricular events, total"""

    PVC = "PVC"
    """Number of single occurrence ectopic beats originating from the ventricles"""

    PVC_COUPLET = "PVC_couplet"
    """Number of couplet ectopic beats originating from the ventricles"""

    PVC_BIGEMINY = "PVC_bigeminy"
    """Ventricular ectopy, bigeminy"""

    PVC_TRIGEMINY = "PVC_trigeminy"
    """Ventricular ectopy, trigeminy"""

    PVC_RUNS = "PVC_runs"
    """Ventricular ectopy, runs"""

    PVC_LONGEST = "PVC_longest"
    """Longest ventricular ectopy episode (beats)"""

    PVC_FASTEST = "PVC_fastest"
    """Fastest ventricular ectopy episode (bpm)"""

    VT = "VT"
    """Presence of ventricular tachycardia"""

    VT_COUNT = "VT_count"
    """Number of distinct ventricular tachycardia episodes"""

    VT_LONGEST = "VT_longest"
    """Time of the longest ventricular tachycardia episode"""

    VT_FASTESTHR = "VT_fastestHR"
    """Heart rate of the fastest ventricular tachycardia episode"""

    PAC_EVENTS = "PAC_events"
    """Supraventricular events, total"""

    PAC = "PAC"
    """Number of single occurrence ectopic beats originating from the atria (total)"""

    PAC_COUPLET = "PAC_couplet"
    """Number of couplet ectopic beats originating from the atria"""

    PAC_BIGEMINY = "PAC_bigeminy"
    """Supraventricular ectopy, bigeminy"""

    PAC_TRIGEMINY = "PAC_trigeminy"
    """Supraventricular ectopy, trigeminy"""

    PAC_RUNS = "PAC_runs"
    """Supraventricular ectopy, runs"""

    PAC_LONGEST = "PAC_longest"
    """Longest supraventricular ectopy episode (beats)"""

    PAC_FASTEST = "PAC_fastest"
    """Fastest supraventricular ectopy episode (bpm)"""

    SVT_YN = "SVT_yn"
    """Presence of supraventricular tachycardia"""

    SVT_COUNT = "SVT_count"
    """Number of distinct supraventricular tachycardia episodes"""

    SVT_LONGEST = "SVT_longest"
    """Time of the longest supraventricular tachycardia episode"""

    SVT_FASTESTHR = "SVT_fastestHR"
    """Heart rate of the fastest supraventricular tachycardia episode"""

    AFIB = "afib"
    """Presence of atrial fibrillation"""

    AFIB_COUNT = "afib_count"
    """Number of afib episodes"""

    AFIB_AVGHR = "afib_avgHR"
    """Average Heart rate in atrial fibrillation (time averaged HR of all afib episodes)"""

    AFIB_LONGEST = "afib_longest"
    """Time of the longest atrial fibrillation episode"""

    AFIB_FASTESTHR = "afib_fastestHR"
    """Heart rate of the fastest atrial fibrillation episode"""

    AFLUT = "aflut"
    """Presence of atrial flutter"""

    AFLUT_COUNT = "aflut_count"
    """Number of atrial flutter episodes"""

    AFLUT_AVGHR = "aflut_avgHR"
    """Average Heart rate in atrial flutter"""

    AFLUT_LONGEST = "aflut_longest"
    """Time of the longest atrial flutter episode"""

    AFLUT_FASTESTHR = "aflut_fastestHR"
    """Heart rate of the fastest atrial flutter episode"""

    PAUSE = "pause"
    """Presence of pause"""

    PAUSE_COUNT = "pause_count"
    """Number of pauses"""

    PAUSE_TIME = "pause_time"
    """Length of time for the longest pause"""

    OTHER_RHYTHM = "other_rhythm"
    """Free text of other observed rhythms"""


@dataclass
class ECGFeatures:
    """Data model for the processed ambulatory ECG data."""

    participant_id: str
    visit_id: str

    tot_time: float
    start_time: datetime
    stop_time: datetime

    total_qrs: int
    max_hr: int
    min_hr: int
    avg_hr: int

    pvc_events: int
    pvc: int
    pvc_couplet: int
    pvc_bigeminy: int
    pvc_trigeminy: int
    pvc_runs: int
    pvc_longest: int
    pvc_fastest: int

    vt_present: bool
    vt_count: int
    vt_longest: int
    vt_fastest_hr: int

    pac_events: int
    pac: int
    pac_couplet: int
    pac_bigeminy: int
    pac_trigeminy: int
    pac_runs: int
    pac_longest: int
    pac_fastest: int

    svt_present: bool
    svt_count: int
    svt_longest: int
    svt_fastest_hr: int

    afib_present: bool
    afib_count: int
    afib_avg_hr: int
    afib_longest: int
    afib_fastest_hr: int

    aflut_present: bool
    aflut_count: int
    aflut_avg_hr: int
    aflut_longest: int
    aflut_fastest_hr: int

    pause_present: bool
    pause_count: int
    pause_time: int

    other_rhythm: str

    @classmethod
    def from_csv(cls, path: Path) -> "ECGFeatures":
        """Reads the ECG features from a CSV file."""
        data = pd.read_csv(path, delimiter="|")
        return cls(
            participant_id=data[ProcessedCSVColumn.PARTICIPANT_ID][0],
            visit_id=data[ProcessedCSVColumn.VISIT_ID][0],
            tot_time=data[ProcessedCSVColumn.TOTAL_TIME][0],
            start_time=datetime.strptime(data[ProcessedCSVColumn.START_TIME][0], "%H:%M:%S"),
            stop_time=datetime.strptime(data[ProcessedCSVColumn.STOP_TIME][0], "%H:%M:%S"),
            total_qrs=data[ProcessedCSVColumn.TOTAL_QRS][0],
            max_hr=data[ProcessedCSVColumn.MAX_HR][0],
            min_hr=data[ProcessedCSVColumn.MIN_HR][0],
            avg_hr=data[ProcessedCSVColumn.AVG_HR][0],
            pvc_events=data[ProcessedCSVColumn.PVC_EVENTS][0],
            pvc=data[ProcessedCSVColumn.PVC][0],
            pvc_couplet=data[ProcessedCSVColumn.PVC_COUPLET][0],
            pvc_bigeminy=data[ProcessedCSVColumn.PVC_BIGEMINY][0],
            pvc_trigeminy=data[ProcessedCSVColumn.PVC_TRIGEMINY][0],
            pvc_runs=data[ProcessedCSVColumn.PVC_RUNS][0],
            pvc_longest=data[ProcessedCSVColumn.PVC_LONGEST][0],
            pvc_fastest=data[ProcessedCSVColumn.PVC_FASTEST][0],
            vt_present=data[ProcessedCSVColumn.VT][0],
            vt_count=data[ProcessedCSVColumn.VT_COUNT][0],
            vt_longest=data[ProcessedCSVColumn.VT_LONGEST][0],
            vt_fastest_hr=data[ProcessedCSVColumn.VT_FASTESTHR][0],
            pac_events=data[ProcessedCSVColumn.PAC_EVENTS][0],
            pac=data[ProcessedCSVColumn.PAC][0],
            pac_couplet=data[ProcessedCSVColumn.PAC_COUPLET][0],
            pac_bigeminy=data[ProcessedCSVColumn.PAC_BIGEMINY][0],
            pac_trigeminy=data[ProcessedCSVColumn.PAC_TRIGEMINY][0],
            pac_runs=data[ProcessedCSVColumn.PAC_RUNS][0],
            pac_longest=data[ProcessedCSVColumn.PAC_LONGEST][0],
            pac_fastest=data[ProcessedCSVColumn.PAC_FASTEST][0],
            svt_present=data[ProcessedCSVColumn.SVT_YN][0],
            svt_count=data[ProcessedCSVColumn.SVT_COUNT][0],
            svt_longest=data[ProcessedCSVColumn.SVT_LONGEST][0],
            svt_fastest_hr=data[ProcessedCSVColumn.SVT_FASTESTHR][0],
            afib_present=data[ProcessedCSVColumn.AFIB][0],
            afib_count=data[ProcessedCSVColumn.AFIB_COUNT][0],
            afib_avg_hr=data[ProcessedCSVColumn.AFIB_AVGHR][0],
            afib_longest=data[ProcessedCSVColumn.AFIB_LONGEST][0],
            afib_fastest_hr=data[ProcessedCSVColumn.AFIB_FASTESTHR][0],
            aflut_present=data[ProcessedCSVColumn.AFLUT][0],
            aflut_count=data[ProcessedCSVColumn.AFLUT_COUNT][0],
            aflut_avg_hr=data[ProcessedCSVColumn.AFLUT_AVGHR][0],
            aflut_longest=data[ProcessedCSVColumn.AFLUT_LONGEST][0],
            aflut_fastest_hr=data[ProcessedCSVColumn.AFLUT_FASTESTHR][0],
            pause_present=data[ProcessedCSVColumn.PAUSE][0],
            pause_count=data[ProcessedCSVColumn.PAUSE_COUNT][0],
            pause_time=data[ProcessedCSVColumn.PAUSE_TIME][0],
            other_rhythm=data[ProcessedCSVColumn.OTHER_RHYTHM][0],
        )
