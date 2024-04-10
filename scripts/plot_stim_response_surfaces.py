"""This script computes and plots the response surfaces of the ANS testing data."""

from collections import defaultdict
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.stats
from scipy.interpolate import griddata
from utils import parse_args

from reveal_data_client import RevealDataClient
from reveal_data_client.constants import VnsStatus
from reveal_data_client.stim_setting import StimSetting, get_ans_stim_mapping

CONFIDENCE_INTERVAL = 0.95


def get_stim_on_times(
    start_time: pd.Timedelta, end_time: pd.Timedelta, stim_setting: StimSetting
) -> Sequence[tuple[pd.Timedelta, pd.Timedelta]]:
    """Get the times when the stimulation is ON.

    :param start_time: The start time of the ANS period.
    :param end_time: The end time of the ANS period.
    :param stim_setting: The stimulation setting.
    :return: A list of tuples with the start and end times when the stimulation is ON.
    """
    # TODO: Get the stimulation ON times using the "stimulator" signal in the ANS data instead.
    #       For now, using the duty cycle for test participants that didnt' have the stimulator
    #       signal.
    stim_on_times = []
    stim_on_time = start_time
    while stim_on_time < end_time:
        stim_on_times.append(
            (stim_on_time, stim_on_time + pd.Timedelta(minutes=stim_setting.duty_cycle_on))
        )
        stim_on_time += pd.Timedelta(minutes=stim_setting.duty_cycle_on) + pd.Timedelta(
            minutes=stim_setting.duty_cycle_off
        )
    return stim_on_times


class PhysioChange:
    """
    This class measures the change in a physiological signal during a stimulation.
    """

    def __init__(
        self,
        stim: StimSetting,
        physio_signal: pd.Series,
        stim_on_times: Sequence[tuple[pd.Timedelta, pd.Timedelta]],
        physio_signal_units: str,
        pre_stim_hr_window_ms: int = 5_000,
        post_stim_hr_window_ms: int = 5_000,
    ):
        self.stim = stim
        self.physio_signal = physio_signal
        self.pre_stim_hr_window_ms = pre_stim_hr_window_ms
        self.post_stim_hr_window_ms = post_stim_hr_window_ms
        self.physio_signal_units = physio_signal_units
        self._stim_on_times = stim_on_times

        self._pre_stim_windows: list[tuple[pd.Timedelta, pd.Timedelta]] = []
        self._post_stim_windows: list[tuple[pd.Timedelta, pd.Timedelta]] = []
        self._baselines: list[float] = []
        self._post_stim_values: list[float] = []
        self._absolute_changes: list[float] = []
        self._relative_changes: list[float] = []

        # Compute the change in physiology for each stimulation ON period
        for stim_start, stim_end in stim_on_times:
            self._compute_physio_change(physio_signal, stim_start, stim_end)

        self._check_number_of_values()

    @property
    def stim_on_times(self) -> Sequence[tuple[pd.Timedelta, pd.Timedelta]]:
        """Get the stimulation ON times."""
        return self._stim_on_times

    @property
    def pre_stim_windows(self) -> Sequence[tuple[pd.Timedelta, pd.Timedelta]]:
        return self._pre_stim_windows

    @property
    def post_stim_windows(self) -> Sequence[tuple[pd.Timedelta, pd.Timedelta]]:
        return self._post_stim_windows

    @property
    def baselines(self) -> Sequence[float]:
        """Get the baseline physio values for each stimulation ON period."""
        return self._baselines

    @property
    def post_stim_values(self) -> Sequence[float]:
        """Get the post-stimulation physio values for each stimulation ON period."""
        return self._post_stim_values

    @property
    def absolute_changes(self) -> Sequence[float]:
        """Get the maximum absolute change in physiology for each stimulation ON period."""
        return self._absolute_changes

    @property
    def changes_percent(self) -> Sequence[float]:
        """
        Get the maximum change in physiology, expressed in percentage, for each stimulation
        ON period.
        """
        return self._relative_changes

    def _check_number_of_values(self) -> None:
        """Check that the number of values is consistent across the internal lists."""
        if (
            len(self._baselines)
            != len(self._post_stim_values)
            != len(self._absolute_changes)
            != len(self._relative_changes)
        ):
            raise ValueError("The number of values is inconsistent.")

    def _compute_physio_change(
        self,
        physio_signal: pd.Series,
        stim_start: pd.Timedelta,
        stim_end: pd.Timedelta,
        pre_stim_window_sec: int = 10,
        post_stim_window_sec: int = 10,
    ) -> None:
        """
        Compute the change in the physiological signal during the stimulation ON period. Append
        the results to the internal lists.

        :param physio_signal: The physiological signal (e.g. HR, BP, etc.)
        :param stim_start: The start time of the stimulation ON period.
        :param stim_end: The end time of the stimulation ON period.
        :param pre_stim_window_sec: The duration of the window to compute the baseline before the
            stimulation ON period.
        :param post_stim_window_sec: The duration of the window to compute the change after the
            stimulation ON period.
        """
        # Get the baseline before the stimulation ON period
        baseline_start = stim_start - pd.Timedelta(seconds=pre_stim_window_sec)
        baseline_end = stim_start
        pre_stim_window = (baseline_start, baseline_end)
        baseline = physio_signal.loc[baseline_start:baseline_end]  # type: ignore
        baseline_mean = baseline.mean()

        # Get the change during the stimulation ON period
        post_stim = (stim_start, stim_end + pd.Timedelta(seconds=post_stim_window_sec))
        post_stim_signal = physio_signal.loc[post_stim[0] : post_stim[1]]  # type: ignore
        post_stim_mean = post_stim_signal.mean()
        is_drop = post_stim_mean < baseline_mean
        post_stim_value = post_stim_signal.min() if is_drop else post_stim_signal.max()
        absolute_change = baseline_mean - post_stim_value
        relative_change = absolute_change / baseline_mean

        # Append the results to the internal lists
        self._pre_stim_windows.append(pre_stim_window)
        self._post_stim_windows.append(post_stim)
        self._baselines.append(baseline_mean)
        self._post_stim_values.append(post_stim_mean)
        self._absolute_changes.append(absolute_change)
        self._relative_changes.append(relative_change)


def plot_physio_change(physio_change: PhysioChange) -> go.Figure:
    """Plot physio change using Plotly.

    :param physio_change: The PhysioChange object containing physio data and stim information.
    :return: The Plotly figure.
    """
    fig = go.Figure()

    # Add the physiological signal to the figure
    fig.add_trace(
        go.Scatter(
            x=physio_change.physio_signal.index.total_seconds(),  # type: ignore
            y=physio_change.physio_signal.values,
            mode="lines",
            name=physio_change.physio_signal.name,
        )
    )

    for i, (stim_start, stim_end) in enumerate(physio_change.stim_on_times):
        # Adding shaded areas for pre-stim, post-stim, and stim windows
        fig.add_vrect(
            x0=stim_start.total_seconds(),
            x1=stim_end.total_seconds(),
            fillcolor="blue",
            opacity=0.1,
            layer="below",
            line_width=0,
            name="Stim Window",
        )
        fig.add_vrect(
            x0=physio_change.pre_stim_windows[i][0].total_seconds(),
            x1=physio_change.pre_stim_windows[i][1].total_seconds(),
            fillcolor="green",
            opacity=0.1,
            layer="below",
            line_width=0,
            name="Pre-Stim Window",
        )
        fig.add_vrect(
            x0=physio_change.post_stim_windows[i][0].total_seconds(),
            x1=physio_change.post_stim_windows[i][1].total_seconds(),
            fillcolor="red",
            opacity=0.1,
            layer="below",
            line_width=0,
            name="Post-Stim Window",
        )

        # Adding horizontal lines for pre-stim and post-stim physio values
        fig.add_hline(
            y=physio_change.baselines[i],
            x0=physio_change.pre_stim_windows[i][0].total_seconds(),
            x1=physio_change.pre_stim_windows[i][1].total_seconds(),
            line={"color": "green", "dash": "dot"},
            name="Pre-Stim hr",
        )
        fig.add_hline(
            y=physio_change.post_stim_values[i],
            x0=physio_change.post_stim_windows[i][0].total_seconds(),
            x1=physio_change.post_stim_windows[i][1].total_seconds(),
            line={"color": "red", "dash": "dot"},
            name="Post-Stim hr",
        )

    # Setting up the title and axes labels
    signal_name = physio_change.physio_signal.name
    fig.update_layout(
        title={
            "text": f"{signal_name} Change <br>Stim: {stim_to_str(physio_change.stim)}",
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis_title="Time (s)",
        yaxis_title=f"{signal_name} ({physio_change.physio_signal_units})",
        showlegend=True,
    )

    # show a legend
    fig.update_layout(showlegend=True)

    return fig


def stim_to_str(stim: StimSetting) -> str:
    """Convert the stimulation setting to a small string."""
    return (
        f"{stim.pulse_width} ms, {stim.current} mA, {stim.frequency} Hz {stim.duty_cycle_off}"
        f"min OFF, {stim.duty_cycle_on} min ON"
    )


def get_surfaces_fig(
    df: pd.DataFrame, x_col: str, y_col: str, z_col: str, title: str, surface_resolution: int = 100
) -> go.Figure:
    """Produces a single plot with one surface for each channel.

    :param df: pandas dataframe with surface data
    :param x_col: name of the column for the x-axis
    :param y_col: name of the column for the y-axis
    :param z_col: name of the column for the z-axis
    :param title: title of the plot
    :param surface_resolution: resolution of the surface plot. Number of points in each axis.
    :return: plotly figure
    """
    fig = go.Figure()

    # Compute confidence intervals
    z_score = scipy.stats.norm.ppf(1 - (1 - CONFIDENCE_INTERVAL) / 2)
    ci = df.groupby([x_col, y_col])[z_col].agg(["mean", "std"]).reset_index()
    ci["ci_low"] = ci["mean"] - z_score * ci["std"]
    ci["ci_high"] = ci["mean"] + z_score * ci["std"]
    ci["ci_low"] = ci["ci_low"].fillna(ci["mean"])
    ci["ci_high"] = ci["ci_high"].fillna(ci["mean"])

    # Generate a regular grid to interpolate the data. Unfortunately, plotly does not support
    # 3D surface plots with irregularly spaced data.
    xi = np.linspace(
        df[x_col].min(),
        df[x_col].max(),
        surface_resolution,
    )
    yi = np.linspace(
        df[y_col].min(),
        df[y_col].max(),
        surface_resolution,
    )
    xi, yi = np.meshgrid(xi, yi)

    # Interpolate z values on the generated grid.
    zi = griddata(
        (ci[x_col], ci[y_col]),
        ci["mean"],
        (xi, yi),
        method="linear",
    )

    ci_low = griddata(
        (ci[x_col], ci[y_col]),
        ci["ci_low"],
        (xi, yi),
        method="linear",
    )

    ci_high = griddata(
        (ci[x_col], ci[y_col]),
        ci["ci_high"],
        (xi, yi),
        method="linear",
    )

    fig.add_trace(
        go.Surface(
            x=xi,
            y=yi,
            z=zi,
            name="mean response",
            showscale=False,
        )
    )

    fig.add_trace(
        go.Surface(
            x=xi,
            y=yi,
            z=ci_low,
            name=f"{CONFIDENCE_INTERVAL} confidence interval",
            showscale=False,
            opacity=0.5,
        )
    )

    fig.add_trace(
        go.Surface(
            x=xi,
            y=yi,
            z=ci_high,
            name=f"{CONFIDENCE_INTERVAL} confidence interval",
            showscale=False,
            opacity=0.5,
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=df[x_col],
            y=df[y_col],
            z=df[z_col],
            mode="markers",
            name="reponses",
            marker={"size": 5},
        )
    )

    fig.update_layout(
        title=title,
        scene={
            "xaxis_title": x_col,
            "yaxis_title": y_col,
            "zaxis_title": z_col,
        },
    ).update_traces(showlegend=True, selector={"type": "surface"})

    return fig


def main(dataset_path: Path) -> None:

    client = RevealDataClient.from_path(dataset_path)

    stim_mapping = get_ans_stim_mapping(dataset_path=dataset_path)

    patient_to_hr_changes = defaultdict(list)
    patient_to_bp_changes = defaultdict(list)
    patient_to_respiratory_rate_changes = defaultdict(list)
    for (participant_id, visit_id, ans_period), stim_setting in stim_mapping.items():

        data_df = client.coarse_time_series.get_data_for_ans_period(
            participant_id=participant_id,
            visit_id=visit_id,
            ans_period=ans_period,
            vns_status=VnsStatus.ON,
        )
        if data_df.empty:
            print(
                f"No data found for participant {participant_id}, visit {visit_id}, ANS period"
                f"{ans_period}"
            )
            continue

        print(f"Participant {participant_id}, Visit {visit_id}, ANS Period {ans_period}")
        print(f"    Stimulation setting: {stim_setting}")

        stim_on_times = get_stim_on_times(data_df.index[0], data_df.index[-1], stim_setting)

        # Compute and plot the HR change
        hr_change = PhysioChange(
            stim=stim_setting,
            physio_signal=data_df["HR"],
            stim_on_times=stim_on_times,
            physio_signal_units="bpm",
        )
        hr_change_fig = plot_physio_change(hr_change)
        hr_change_fig.write_html(
            f"participant_{participant_id}_visit_{visit_id}_ans_period_{ans_period}_hr_change.html"
        )
        patient_to_hr_changes[participant_id].append(hr_change)

        # Compute and plot the BP change
        bp_change = PhysioChange(
            stim=stim_setting,
            physio_signal=data_df["Mean"],
            stim_on_times=stim_on_times,
            physio_signal_units="mmHg",
        )
        bp_change_fig = plot_physio_change(bp_change)
        bp_change_fig.write_html(
            f"participant_{participant_id}_visit_{visit_id}_ans_period_{ans_period}_bp_change.html"
        )
        patient_to_bp_changes[participant_id].append(bp_change)

        # Compute and plot respiration rate change
        respiratory_rate_change = PhysioChange(
            stim=stim_setting,
            physio_signal=data_df["Respiratory Rate"],
            stim_on_times=stim_on_times,
            physio_signal_units="bpm",
        )
        respiratory_rate_change_fig = plot_physio_change(respiratory_rate_change)
        respiratory_rate_change_fig.write_html(
            f"participant_{participant_id}_visit_{visit_id}_ans_period_{ans_period}"
            "_respiratory_rate_change.html"
        )
        patient_to_respiratory_rate_changes[participant_id].append(respiratory_rate_change)

    # Plot response surfaces for each participant
    for participant_id, hr_changes in patient_to_hr_changes.items():
        df_dict: dict[str, list[int | float]] = defaultdict(list)
        for hr_change in hr_changes:
            for absolute_change in hr_change.absolute_changes:
                df_dict["Frequency (Hz)"].append(hr_change.stim.frequency)
                df_dict["Duty Cycle Off (min)"].append(hr_change.stim.duty_cycle_off)
                df_dict["Heart Rate Change (bpm)"].append(absolute_change)
        hr_df = pd.DataFrame(df_dict)
        hr_fig = get_surfaces_fig(
            df=hr_df,
            x_col="Frequency (Hz)",
            y_col="Duty Cycle Off (min)",
            z_col="Heart Rate Change (bpm)",
            title=f"HR Change for Participant {participant_id}",
        )
        hr_fig.write_html(f"participant_{participant_id}_hr_change_surface.html")

    for participant_id, bp_changes in patient_to_bp_changes.items():
        df_dict = defaultdict(list)
        for bp_change in bp_changes:
            for absolute_change in bp_change.absolute_changes:
                df_dict["Frequency (Hz)"].append(bp_change.stim.frequency)
                df_dict["Duty Cycle Off (min)"].append(bp_change.stim.duty_cycle_off)
                df_dict["Mean BP Change (mmHg)"].append(absolute_change)
        bp_df = pd.DataFrame(df_dict)
        bp_fig = get_surfaces_fig(
            df=bp_df,
            x_col="Frequency (Hz)",
            y_col="Duty Cycle Off (min)",
            z_col="Mean BP Change (mmHg)",
            title=f"Mean BP Change for Participant {participant_id}",
        )
        bp_fig.write_html(f"participant_{participant_id}_bp_change_surface.html")

    for participant_id, respiratory_rate_changes in patient_to_respiratory_rate_changes.items():
        df_dict = defaultdict(list)
        for respiratory_rate_change in respiratory_rate_changes:
            for absolute_change in respiratory_rate_change.absolute_changes:
                df_dict["Frequency (Hz)"].append(respiratory_rate_change.stim.frequency)
                df_dict["Duty Cycle Off (min)"].append(respiratory_rate_change.stim.duty_cycle_off)
                df_dict["Respiratory Rate Change (bpm)"].append(absolute_change)
        respiratory_rate_df = pd.DataFrame(df_dict)
        respiratory_rate_fig = get_surfaces_fig(
            df=respiratory_rate_df,
            x_col="Frequency (Hz)",
            y_col="Duty Cycle Off (min)",
            z_col="Respiratory Rate Change (bpm)",
            title=f"Respiratory Rate Change for Participant {participant_id}",
        )
        respiratory_rate_fig.write_html(
            f"participant_{participant_id}_respiratory_rate_change_surface.html"
        )


if __name__ == "__main__":
    args = parse_args()
    main(Path(args.dataset_path))
