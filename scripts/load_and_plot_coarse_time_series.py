"""Loads and plot coarse time-series data from the Reveal dataset."""

import argparse
import logging
from pathlib import Path

import plotly.express as px

from reveal_data_client import RevealDataClient

LOG = logging.getLogger(__name__)

PLOT_DIR = "plots"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Load and plot coarse time-series data from the Reveal dataset."
    )
    parser.add_argument(
        "dataset_path",
        type=Path,
        help="Path to the root directory of the Reveal dataset.",
    )
    return parser.parse_args()


def main(dataset_path: Path) -> None:
    logging.basicConfig(level=logging.INFO)

    # Make sure the plot directory exists
    repo_root_dir = Path(__file__).parent.parent
    plot_dir = repo_root_dir / PLOT_DIR
    plot_dir.mkdir(exist_ok=True)

    # Load and plot the data
    client = RevealDataClient.from_path(dataset_path)
    participant_ids = client.get_participant_ids()
    for participant_id in participant_ids:
        print(f"participant_ids : {participant_id}")
        visit_ids = client.get_visit_ids(participant_id)
        for visit_id in visit_ids:
            for ans_period in client.get_ans_periods(participant_id, visit_id):
                for is_vns_on in [True, False]:
                    df = client.coarse_time_series.get_data_for_ans_period(
                        participant_id, visit_id, ans_period, is_vns_on
                    )
                    if len(df) == 0:
                        continue
                    elapsed = df.index[-1] - df.index[0]
                    sampling_rate = len(df) / elapsed.total_seconds()
                    df = df.select_dtypes(include="number")  # Select only numerical columns
                    df.index = (
                        df.index.total_seconds()
                    )  # Plotly express does not support timedelta index
                    fig = px.line(
                        df, x=df.index, y=df.columns, title=f"{participant_id}_{visit_id}"
                    )
                    fig_path = (
                        plot_dir
                        / f"{participant_id}_{visit_id.value}_{ans_period.value}_{is_vns_on}.html"
                    )
                    fig.write_html(fig_path)
                    LOG.info(
                        f"Plotting participant {participant_id}, visit {visit_id}, ANS period "
                        f'{ans_period}, VNS {"ON" if is_vns_on else "OFF"}.\n'
                        f"Elapsed time: {elapsed}, sampling rate: {sampling_rate} Hz.\n"
                        f"Plot saved to {fig_path}\n"
                    )


if __name__ == "__main__":
    args = parse_args()
    main(Path(args.dataset_path))
