"""Run the full simulation and write raw estimates to disk."""

import argparse
import logging
import os
import time

import numpy as np
import pandas as pd
from tqdm import tqdm

from . import config, dgps, methods

logger = logging.getLogger(__name__)


def cells(scenario):
    """The estimator configurations to run for one scenario."""
    extensions = (config.EXTENSION_ESTIMATORS
                  if scenario in config.EXTENSION_SCENARIOS else [])
    return config.ESTIMATORS + extensions


def run_replicate(scenario, replicate, seed, n):
    """Draw one dataset and return every estimate computed on it.

    All estimators within a replicate see the same data, so differences between
    them are not confounded with the draw.  The seed is passed in rather than
    derived here, so a single replicate can be rerun on its own.
    """
    data = dgps.generate(scenario, n, np.random.default_rng(seed))
    return [
        {
            "scenario": scenario,
            "replicate": replicate,
            "estimator": name,
            "estimate": methods.estimate(data, scenario, family, ps_name, or_name),
        }
        for name, family, ps_name, or_name in cells(scenario)
    ]


def run(scenarios, n, n_sim, master_seed, out_path):
    """Run every scenario and write a long-format CSV of all estimates."""
    # One child sequence per scenario, indexed against the full scenario list
    # rather than the requested subset, so that a single scenario can be rerun
    # on its own and still draw the same data.  Child seeds are determined by
    # position, so a short run reproduces the leading replicates of a long one.
    all_scenarios = list(config.SCENARIOS)
    seeds = np.random.SeedSequence(master_seed).spawn(len(all_scenarios))

    records = []
    for scenario in scenarios:
        seed_sequence = seeds[all_scenarios.index(scenario)].spawn(n_sim)

        started = time.perf_counter()
        for replicate in tqdm(range(n_sim), desc=f"scenario {scenario}", unit="rep"):
            records.extend(run_replicate(scenario, replicate, seed_sequence[replicate], n))
        logger.info("scenario %s: %d replicates in %.1fs",
                    scenario, n_sim, time.perf_counter() - started)

    raw = pd.DataFrame.from_records(records)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    raw.to_csv(out_path, index=False)
    logger.info("wrote %d estimates to %s", len(raw), out_path)
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=config.RAW_PATH)
    parser.add_argument("--n", type=int, default=config.N)
    parser.add_argument("--n-sim", type=int, default=config.N_SIM)
    parser.add_argument("--seed", type=int, default=config.MASTER_SEED)
    parser.add_argument("--scenario", action="append", dest="scenarios")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    run(args.scenarios or list(config.SCENARIOS),
        args.n, args.n_sim, args.seed, args.out)


if __name__ == "__main__":
    main()
