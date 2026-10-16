"""Summarise raw estimates into the performance table."""

import argparse
import logging
import os

import pandas as pd

from . import config, metrics

logger = logging.getLogger(__name__)

MEASURES = ["bias_mean", "bias_median", "variance", "iqr"]


def load(raw_path):
    if not os.path.exists(raw_path):
        raise SystemExit(f"{raw_path} not found; run `make simulate` first")
    return pd.read_csv(raw_path)


def summarise(raw):
    truths = {name: spec["truth"] for name, spec in config.SCENARIOS.items()}
    return metrics.summarise(raw, truths, config.PUBLISHED)


def comparison_table(summary):
    """The reproduction cells, each measure shown beside its published value."""
    core = summary[summary["published_bias_mean"].notna()].copy()
    table = core[["scenario", "estimator"]].copy()
    for measure in MEASURES:
        table[measure] = core[measure].map("{:.3f}".format)
        table["paper_" + measure] = core["published_" + measure].map("{:.2f}".format)
        table["z_" + measure] = core["z_" + measure].map("{:+.1f}".format)
    return table


def extension_table(summary):
    """The constrained-variant cells, which have no published counterpart."""
    extra = summary[summary["published_bias_mean"].isna()]
    return extra[["scenario", "estimator"] + MEASURES]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", default=config.RAW_PATH)
    parser.add_argument("--out", default=config.SUMMARY_PATH)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    summary = summarise(load(args.raw))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    summary.to_csv(args.out, index=False)
    logger.info("wrote %d cells to %s", len(summary), args.out)

    fmt = {"float_format": lambda x: f"{x: .3f}", "index": False, "na_rep": "-"}
    print("\nReproduction cells, against Table 2")
    print(comparison_table(summary).to_string(**fmt))

    extensions = extension_table(summary)
    if not extensions.empty:
        print("\nExtension cells: the phi1 = phi2 variant of Section 2.2")
        print(extensions.to_string(**fmt))

    worst = summary["z_bias_mean"].abs().max()
    print(f"\nLargest absolute z for the bias across reproduction cells: {worst:.1f}")


if __name__ == "__main__":
    main()
