from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def fit_beta_from_csv(csv_path: str | Path) -> float:
    """
    Read amplitude_scaling CSV and fit beta in A ~ W^{-beta}.

    Assumes CSV with header: Wcoh,A,omega_c
    """
    csv_path = Path(csv_path)
    data = np.genfromtxt(csv_path, delimiter=",", names=True)

    W = data["Wcoh"]
    A = data["A"]

    # keep strictly positive A values to avoid log(0)
    mask = A > 0.0
    W = W[mask]
    A = A[mask]

    if W.size < 2:
        raise RuntimeError(
            f"Need at least 2 data points to fit beta; got {W.size} from {csv_path}"
        )

    logW = np.log(W)
    logA = np.log(A)

    # log A = m log W + c, with A ~ C W^{-beta} => beta = -m
    m, c = np.polyfit(logW, logA, 1)
    beta = -m
    return float(beta)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Fit beta from amplitude_scaling_soft_rudder.csv",
    )
    parser.add_argument(
        "csv",
        type=str,
        help="Path to amplitude_scaling_soft_rudder.csv",
    )
    args = parser.parse_args(argv)

    beta = fit_beta_from_csv(args.csv)
    print(f"Fitted beta (A ~ W^(-beta)): beta = {beta:.6g}")


if __name__ == "__main__":
    main()