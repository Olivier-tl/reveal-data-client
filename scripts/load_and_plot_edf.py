"""Test script to load ANS testing data from EDF files and display it."""

import argparse
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from pyedflib import EdfReader


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Load and plot coarse time-series data from the Reveal dataset."
    )
    parser.add_argument(
        "edf_file_path",
        type=Path,
        help="Path to the EDF file containing the ANS testing data.",
    )
    return parser.parse_args()


def load_and_plot_edf(edf_file_path: Path) -> None:

    print("Reading EDF file %s" % edf_file_path)
    f = EdfReader(str(edf_file_path))
    figure = go.Figure()
    for i in np.arange(f.signals_in_file):

        # Load the signal
        signal = f.readSignal(i)
        signal_label = f.getLabel(i)

        # Get the time axis
        signal_duration = f.getFileDuration()
        signal_sample_rate = f.getSampleFrequency(i)
        signal_time = np.linspace(0, signal_duration, signal.shape[0])

        # Get signal metadata
        signal_metadata = f.getSignalHeader(i)

        # If the signal has a sampling rate higher than 250Hz, downsample it to 250Hz for plotting
        if signal_sample_rate > 250:
            signal = signal[:: int(signal_sample_rate / 250)]
            signal_time = signal_time[:: int(signal_sample_rate / 250)]
            signal_sample_rate = 250

        # plot the signal
        figure.add_trace(go.Scatter(x=signal_time, y=signal, mode="lines", name=signal_label))

        print(
            f"Plotted signal {signal_label} ({signal_sample_rate} Hz) with metadata {signal_metadata}"
        )

    figure.update_layout(title="ANS Testing Data", xaxis_title="Time (s)", yaxis_title="Amplitude")

    # Save the plot to html
    file_name = edf_file_path.stem + ".html"
    figure.write_html(file_name)


if __name__ == "__main__":
    args = parse_args()
    load_and_plot_edf(args.edf_file_path)
