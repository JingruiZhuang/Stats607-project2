"""Build the figures from the raw estimates and the summary table."""

import argparse
import logging
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import analyze, config

logger = logging.getLogger(__name__)

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SOFT = "#52514e"
GRID = "#dcdbd6"

# Categorical slots 1, 3 and 7 of the reference palette, validated all-pairs in
# light mode.  Colour follows the estimator family, never its rank in a figure.
FAMILY_COLOUR = {"HT": "#2a78d6", "OR": "#eb6834", "DR": "#1baf7a", "DR1": "#6250d6"}

FAMILY_LABEL = {
    "HT": "Horvitz-Thompson",
    "OR": "outcome regression",
    "DR": "doubly robust",
    "DR1": "doubly robust, coefficients constrained equal",
}

MARK = "·"


def style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.edgecolor": GRID,
        "xtick.color": INK_SOFT,
        "ytick.color": INK_SOFT,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 9,
        "axes.titlesize": 10,
        "figure.dpi": 200,
    })


def family_handles(stems):
    """Legend entries naming each estimator family beside its colour."""
    return [plt.Line2D([], [], marker="s", linestyle="none", markersize=8,
                       color=FAMILY_COLOUR[stem], label=FAMILY_LABEL[stem])
            for stem in stems]


def family(estimator):
    return estimator.split(".")[0]


def cell_label(ps_name, or_name):
    """A one-line reading of which nuisance models this cell got right."""
    mark = {"ps_true": "correct", "ps_false": "false", None: "unused",
            "or_true": "correct", "or_false": "false"}
    return f"PS {mark[ps_name]}, OR {mark[or_name]}"


def ordered_cells(scenario):
    cells = config.ESTIMATORS + (config.EXTENSION_ESTIMATORS
                                 if scenario in config.EXTENSION_SCENARIOS else [])
    return [c for c in cells]


def plot_distributions(raw, out_path):
    """Diagnostic: the sampling distribution behind every number in Table 2.

    A table of biases and variances cannot show shape.  These boxplots do, and
    they expose the heavy tails of the doubly robust estimator under a false
    outcome model that the variance column reports but does not convey.
    """
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.9))

    for ax, scenario in zip(axes, config.SCENARIOS):
        names = [c[0] for c in config.ESTIMATORS]
        truth = config.SCENARIOS[scenario]["truth"]
        values = [raw.loc[(raw.scenario == scenario) & (raw.estimator == n),
                          "estimate"].to_numpy() for n in names]

        positions = np.arange(len(names))
        boxes = ax.boxplot(values, positions=positions, orientation="horizontal",
                           widths=0.62,
                           whis=(5, 95), patch_artist=True, showfliers=True,
                           medianprops=dict(color=SURFACE, linewidth=1.6),
                           whiskerprops=dict(color=INK_SOFT, linewidth=1.0),
                           capprops=dict(color=INK_SOFT, linewidth=1.0),
                           flierprops=dict(marker="o", markersize=2.2,
                                           markerfacecolor=INK_SOFT, alpha=0.28,
                                           markeredgecolor="none"))
        for patch, name in zip(boxes["boxes"], names):
            patch.set_facecolor(FAMILY_COLOUR[family(name)])
            patch.set_edgecolor(SURFACE)
            patch.set_linewidth(1.6)

        ax.axvline(truth, color=INK, linewidth=1.2, linestyle=(0, (4, 3)), zorder=0)
        ax.annotate(f"truth = {truth:g}", xy=(truth, -0.46),
                    xytext=(5, 0), textcoords="offset points",
                    fontsize=8, color=INK_SOFT, va="center")

        ax.set_yticks(positions)
        ax.set_yticklabels(names)
        ax.set_ylim(len(names) - 0.4, -0.75)
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_xlabel("estimate")
        ax.set_title(f"Scenario {scenario}: {config.SCENARIOS[scenario]['label']}",
                     loc="left", color=INK)

    fig.legend(handles=family_handles(["HT", "OR", "DR"]), loc="lower left",
               bbox_to_anchor=(0.005, 0.0), ncol=3, frameon=False, fontsize=8,
               labelcolor=INK_SOFT)
    fig.suptitle("Sampling distributions over 1000 replicates, n = 500",
                 x=0.005, ha="left", fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(out_path)
    plt.close(fig)
    logger.info("wrote %s", out_path)


def plot_bias_grid(summary, out_path):
    """Publication: bias against the published value, cell by cell.

    Each cell is labelled with which nuisance models it got right, so the claim
    that the doubly robust estimator needs only one of them can be read off the
    figure instead of inferred from a table of estimator names.
    """
    core = summary[summary["published_bias_mean"].notna()]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.4))

    for ax, scenario in zip(axes, config.SCENARIOS):
        cells = [c for c in config.ESTIMATORS]
        rows = core[core.scenario == scenario].set_index("estimator")
        positions = np.arange(len(cells))

        for position, (name, _, ps_name, or_name) in zip(positions, cells):
            row = rows.loc[name]
            colour = FAMILY_COLOUR[family(name)]
            ax.errorbar(row["bias_mean"], position,
                        xerr=1.96 * row["bias_mean_se"],
                        fmt="o", markersize=7, color=colour,
                        markeredgecolor=SURFACE, markeredgewidth=1.4,
                        elinewidth=2, capsize=0, zorder=3)
            ax.plot(row["published_bias_mean"], position, marker="D",
                    markersize=6.5, markerfacecolor="none", markeredgecolor=INK,
                    markeredgewidth=1.2, linestyle="none", zorder=2)

        ax.axvline(0.0, color=INK, linewidth=1.2, zorder=1)
        ax.set_yticks(positions)
        ax.set_yticklabels([f"{name}\n{cell_label(ps, orm)}"
                            for name, _, ps, orm in cells], fontsize=8)
        ax.invert_yaxis()
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_xlabel("bias")
        ax.set_title(f"Scenario {scenario}: {config.SCENARIOS[scenario]['label']}",
                     loc="left", color=INK)

    handles = family_handles(["HT", "OR", "DR"]) + [
        plt.Line2D([], [], marker="o", linestyle="none", markersize=7,
                   color=INK_SOFT, markeredgecolor=SURFACE,
                   label="this study, 95% Monte Carlo interval"),
        plt.Line2D([], [], marker="D", linestyle="none", markersize=6.5,
                   markerfacecolor="none", markeredgecolor=INK,
                   label="Bang and Robins (2005), Table 2"),
    ]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.005, 0.0),
               ncol=3, frameon=False, fontsize=8, labelcolor=INK_SOFT)
    fig.suptitle("Bias of each estimator, against the published values",
                 x=0.005, ha="left", fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0.11, 1, 0.94))
    fig.savefig(out_path)
    plt.close(fig)
    logger.info("wrote %s", out_path)


def plot_extension(summary, out_path):
    """The variant of Section 2.2 beside the estimator that Table 2 reports.

    The two coincide wherever the outcome model is correct and part company
    wherever it is not, which is the only place double robustness is of any use.
    """
    cells = [("or_true", "ps_true", "both models\ncorrect"),
             ("or_false", "ps_true", "outcome model\nfalse"),
             ("or_true", "ps_false", "propensity model\nfalse"),
             ("or_false", "ps_false", "both models\nfalse")]
    suffix = {("ps_true", "or_true"): "", ("ps_true", "or_false"): ".ofal",
              ("ps_false", "or_true"): ".pfal", ("ps_false", "or_false"): ".o+pfal"}

    rows = summary[summary.scenario == "B"].set_index("estimator")
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    positions = np.arange(len(cells))
    offset = 0.13

    for stem, shift in (("DR", -offset), ("DR1", offset)):
        colour = FAMILY_COLOUR[stem]
        xs, ys = [], []
        for position, (or_name, ps_name, _) in zip(positions, cells):
            row = rows.loc[stem + suffix[(ps_name, or_name)]]
            xs.append(position + shift)
            ys.append(row["bias_mean"])
            ax.errorbar(position + shift, row["bias_mean"],
                        yerr=1.96 * row["bias_mean_se"], fmt="o", markersize=8,
                        color=colour, markeredgecolor=SURFACE,
                        markeredgewidth=1.4, elinewidth=2, capsize=0, zorder=3)
        ax.annotate(stem, xy=(xs[-1], ys[-1]), xytext=(10, 0),
                    textcoords="offset points", color=colour, fontsize=9,
                    va="center", fontweight="bold")

    for position, (or_name, ps_name, _) in zip(positions, cells):
        row = rows.loc["DR1" + suffix[(ps_name, or_name)]]
        if abs(row["bias_mean"]) > 0.5:
            ax.annotate(f"{row['bias_mean']:.2f}",
                        xy=(position + offset, row["bias_mean"]),
                        xytext=(0, -14), textcoords="offset points",
                        ha="center", fontsize=8, color=FAMILY_COLOUR["DR1"])

    ax.axhline(0.0, color=INK, linewidth=1.2, zorder=1)
    bottom, top = ax.get_ylim()
    ax.set_ylim(bottom - 0.28, top)
    ax.set_xticks(positions)
    ax.set_xticklabels([label for _, _, label in cells], fontsize=8.5)
    ax.set_xlim(-0.5, len(cells) - 0.25)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_ylabel("bias in estimating the average treatment effect")
    ax.set_title("Scenario B: constraining the two augmentation coefficients\n"
                 "costs double robustness", loc="left", color=INK)
    ax.legend(handles=family_handles(["DR", "DR1"]), loc="upper left",
              frameon=False, fontsize=8, labelcolor=INK_SOFT)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    logger.info("wrote %s", out_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", default=config.RAW_PATH)
    parser.add_argument("--summary", default=config.SUMMARY_PATH)
    parser.add_argument("--outdir", default=config.FIGURE_DIR)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    style()
    os.makedirs(args.outdir, exist_ok=True)

    raw = analyze.load(args.raw)
    summary = (pd.read_csv(args.summary) if os.path.exists(args.summary)
               else analyze.summarise(raw))

    plot_distributions(raw, os.path.join(args.outdir, "distributions.png"))
    plot_bias_grid(summary, os.path.join(args.outdir, "bias_grid.png"))
    plot_extension(summary, os.path.join(args.outdir, "extension.png"))


if __name__ == "__main__":
    main()
