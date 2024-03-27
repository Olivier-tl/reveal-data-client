"""Script to load and display ambulatory data from the Reveal dataset (version 3.19.2024)"""

from ast import literal_eval
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import parse_args

from reveal_data_client.ambulatory import BPFeatures, ECGFeatures

PARTICIPANT_ID = "Sample-001"


def extract_ecg(df: pd.DataFrame) -> pd.Series:
    """
    Returns a series with the ECG data in mV.
    """
    # Each row of the `ECG` column is a list of ECG samples, e.g. [0.86, 1.1, 0.93, ...]
    # We convert from string to list using a literal eval
    ecg_col = df["ECG"].apply(lambda x: literal_eval(x))

    # Flatten the sequence of lists into a single list, and convert to mV
    magnifications = df["Magnification"]
    assert len(set(magnifications)) == 1, "Magnification is not constant"
    ecg = [sample / magnifications[0] for sublist in ecg_col for sample in sublist]

    # Check that the expected sampling rate is constant
    expected_sampling_rates = df["Sample Frequency"]
    assert len(set(expected_sampling_rates)) == 1, "Expected sampling rate is not constant"

    # Check that the actual sampling rate is as expected
    samples_per_seconds = [len(sublist) for sublist in ecg_col]
    assert len(set(samples_per_seconds)) == 1, "Actual sampling rate is not constant"
    assert (
        samples_per_seconds[0] == expected_sampling_rates[0]
    ), "Actual sampling rate is not as expected"

    # Create a time axis in seconds
    time_axis_seconds = [i / samples_per_seconds[0] for i in range(len(ecg))]

    return pd.Series(ecg, index=time_axis_seconds)


def extract_accelerometer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a dataframe with the columns "x", "y", "z" containing the accelerometer data.
    """
    # Each row of the `ACC` column is a list of accelerometer samples. Each sample is a dictionary
    # with keys "x", "y", "z", e.g. [{"x": 0.1, "y": 0.2, "z": 0.3}, ...]
    # We convert from string to list of dictionaries using a literal eval
    accelerometer_col = df["ACC"].apply(lambda x: literal_eval(x))

    # Flatten the sequence of dictionaries into a single list of dictionaries
    accelerometer_data: list[dict[str, float]] = [
        sample for dict_list in accelerometer_col for sample in dict_list
    ]

    # Check that the number of samples per second is constant
    samples_per_seconds = [len(dict_list) for dict_list in accelerometer_col]
    assert len(set(samples_per_seconds)) == 1, "Number of samples per second is not constant"

    # Create a time axis in seconds
    time_axis = [i / samples_per_seconds[0] for i in range(len(accelerometer_data))]
    accelerometer_df = pd.DataFrame(accelerometer_data, index=time_axis)

    return accelerometer_df


def display_ambulatory_ecg_data(ambulatory_ecg_file_path: Path) -> None:
    # Load data
    raw_ecg_data = pd.read_csv(ambulatory_ecg_file_path, delimiter="|")

    # Extract ECG and accelerometer data
    ecg = extract_ecg(raw_ecg_data)
    acc_df = extract_accelerometer(raw_ecg_data)

    # Plot ECG sample
    first_10_sec = ecg.loc[:10]  # First 10 seconds
    fig = px.line(x=first_10_sec.index, y=first_10_sec, title=f"ECG sample", markers=False)
    fig.update_layout(xaxis_title="Time (s)", yaxis_title="ECG (mV)")
    fig.write_html(f"ecg_sample.html")

    # Plot accelerometer sample
    accelerometer_sample = acc_df.loc[:10]  # First 10 seconds
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=accelerometer_sample.index, y=accelerometer_sample["x"], name="x"))
    fig.add_trace(go.Scatter(x=accelerometer_sample.index, y=accelerometer_sample["y"], name="y"))
    fig.add_trace(go.Scatter(x=accelerometer_sample.index, y=accelerometer_sample["z"], name="z"))
    fig.update_layout(
        title=f"Accelerometer sample", xaxis_title="Time (s)", yaxis_title="Acceleration"
    )
    fig.write_html("accelerometer_sample.html")

    # Plot other raw data
    raw_ecg_data.set_index("recordTime", inplace=True)
    raw_ecg_data = raw_ecg_data.select_dtypes(include="number")
    fig = px.line(
        raw_ecg_data, x=raw_ecg_data.index, y=raw_ecg_data.columns, title=f"Ambulatory ECG data"
    )
    fig.update_layout(xaxis_title="Time", yaxis_title="Value")
    fig.write_html("ambulatory_ecg_data.html")


def display_ambulatory_bp_data(ambulatory_bp_file_path: Path) -> None:
    # Load data
    raw_bp_data = pd.read_csv(ambulatory_bp_file_path, delimiter="|")

    # Plot the raw data
    raw_bp_data.set_index("Recording_Day_Time", inplace=True)
    raw_bp_data = raw_bp_data.select_dtypes(include="number")
    fig = px.line(
        raw_bp_data, x=raw_bp_data.index, y=raw_bp_data.columns, title=f"Ambulatory BP data"
    )
    fig.update_layout(xaxis_title="Time", yaxis_title="Value")
    fig.write_html("ambulatory_bp_data.html")


def main(dataset_path: Path) -> None:
    participant_path = dataset_path / "primary" / f"sub-{PARTICIPANT_ID}"
    ambulatory_ecg_file = participant_path / "Ambulatory ECG" / f"{PARTICIPANT_ID}_lab_amb_ecg.csv"
    ambulatory_bp_file = participant_path / "Ambulatory BP" / f"{PARTICIPANT_ID}_lab_amb_bp.csv"
    processed_ambulatory_ecg = ambulatory_ecg_file.with_name(
        ambulatory_ecg_file.stem + "_processed.csv"
    )
    processed_ambulatory_bp = ambulatory_bp_file.with_name(
        ambulatory_bp_file.stem + "_processed.csv"
    )

    # Display ECG and BP features
    ecg_features = ECGFeatures.from_csv(processed_ambulatory_ecg)
    bp_features = BPFeatures.from_csv(processed_ambulatory_bp)
    print("ECG Processed Features : ", asdict(ecg_features))
    print("BP Processed Features : ", asdict(bp_features))

    # Display ECG data
    display_ambulatory_ecg_data(ambulatory_ecg_file)

    # Display BP data
    display_ambulatory_bp_data(ambulatory_bp_file)


if __name__ == "__main__":
    args = parse_args()
    main(args.dataset_path)
