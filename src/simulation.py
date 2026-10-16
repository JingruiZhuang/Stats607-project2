"""Run the full simulation and write raw estimates to disk."""

import argparse
import logging


def run_replicate(scenario, rep, seed):
    """Draw one dataset and return all eight estimates as records."""
    raise NotImplementedError


def run(scenarios, n, n_sim, master_seed, out_path):
    """Run every scenario and write a long-format CSV of all estimates."""
    raise NotImplementedError


def main():
    raise NotImplementedError


if __name__ == "__main__":
    main()
