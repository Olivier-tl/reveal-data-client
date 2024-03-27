import argparse
from pathlib import Path


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
