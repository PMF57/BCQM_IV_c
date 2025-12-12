from __future__ import annotations

from pathlib import Path

import numpy as np

from .config import load_config, Config
from .model import SoftRudderModel
from .spectra import estimate_psd, amplitude_and_omega_c


def run_scan(config_path: str | Path):
    """
    Run a W_coh scan using the soft-rudder kernel.

    Returns arrays (wcoh_values, A_values, omega_c_values).
    Also writes per-W_coh spectra as NPZ and a CSV file with amplitudes.
    """
    cfg: Config = load_config(config_path)
    sim = cfg.simulation
    scan = cfg.scan
    slip = cfg.slip
    out = cfg.output

    base_dir = Path(out.base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    model = SoftRudderModel(law=slip.law, params=slip.params)

    rng_master = np.random.default_rng(sim.seed)

    wcoh_values = np.array(scan.wcoh_values, dtype=float)
    A_values = np.zeros_like(wcoh_values, dtype=float)
    omega_c_values = np.zeros_like(wcoh_values, dtype=float)

    # Debug print so we can see what the scan actually is
    print("Scanning W_coh values:", wcoh_values)

    for i, wcoh in enumerate(wcoh_values):
        # independent RNG for each W_coh for reproducibility
        rng = np.random.default_rng(rng_master.integers(0, 2**63 - 1))

        psd_list = []
        for _ in range(sim.n_ensembles):
            x, v = model.simulate_trajectory(
                wcoh=wcoh,
                n_steps=sim.n_steps,
                rng=rng,
            )
            a = model.acceleration_from_positions(x)
            omega, S = estimate_psd(a, dt=sim.dt)
            psd_list.append(S)

        S_mean = np.mean(np.vstack(psd_list), axis=0)
        A, omega_c = amplitude_and_omega_c(omega, S_mean)
        A_values[i] = A
        omega_c_values[i] = omega_c

        print(f"W_coh = {wcoh:g}: A = {A:.7g}, omega_c = {omega_c:.6g}")

        np.savez(
            base_dir / f"Wcoh_{wcoh:g}.npz",
            omega=omega,
            S=S_mean,
            wcoh=wcoh,
        )

    # write CSV for amplitude scaling
    csv_path = base_dir / "amplitude_scaling_soft_rudder.csv"
    with csv_path.open("w") as f:
        f.write("Wcoh,A,omega_c\n")
        for w, A, oc in zip(wcoh_values, A_values, omega_c_values):
            f.write(f"{w:.6g},{A:.16e},{oc:.16e}\n")

    return wcoh_values, A_values, omega_c_values
