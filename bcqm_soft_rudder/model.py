from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

import numpy as np


@dataclass
class SoftRudderModel:
    """Single-thread soft-rudder binary hop kernel.

    v_{n+1} = v_n with probability p_stay(W_coh)
            = -v_n otherwise
    x_{n+1} = x_n + v_n

    The slip law p_stay(W_coh) is controlled by a 'law' string and a
    parameter dictionary. A few simple options are implemented; you can
    add more as needed.
    """

    law: str
    params: Dict[str, Any]

    def p_stay(self, wcoh: float) -> float:
        law = self.law.lower()
        p = 0.9  # default fallback

        if law == "exp":
            # p_stay = p_max - (p_max - p_min) * exp(-W/W_ref)
            p_min = float(self.params.get("p_min", 0.5))
            p_max = float(self.params.get("p_max", 0.999))
            w_ref = float(self.params.get("w_ref", 10.0))
            p = p_max - (p_max - p_min) * np.exp(-wcoh / w_ref)

        elif law == "rational":
            # p_stay = p_min + (p_max - p_min) * W^alpha / (W^alpha + W0^alpha)
            p_min = float(self.params.get("p_min", 0.5))
            p_max = float(self.params.get("p_max", 0.999))
            w0 = float(self.params.get("w0", 10.0))
            alpha = float(self.params.get("alpha", 1.0))
            num = wcoh**alpha
            den = num + w0**alpha
            frac = num / den if den > 0 else 0.0
            p = p_min + (p_max - p_min) * frac

        elif law == "tanh":
            # p_stay = p_mid + delta * tanh((W - W0)/W_scale)
            p_mid = float(self.params.get("p_mid", 0.75))
            delta = float(self.params.get("delta", 0.24))
            w0 = float(self.params.get("w0", 20.0))
            w_scale = float(self.params.get("w_scale", 10.0))
            p = p_mid + delta * np.tanh((wcoh - w0) / w_scale)

        elif law == "inv":
            # p_stay = 1 - k / W, with clipping for safety
            # This gives flip probability q(W) = k / W,
            # i.e. roughly one direction flip per W-coh steps (for k ~ O(1)).
            k = float(self.params.get("k", 2.0))
            p = 1.0 - k / float(wcoh)

        # clip for safety
        return float(np.clip(p, 0.0, 1.0))

    def simulate_trajectory(self, wcoh: float, n_steps: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
        """Simulate a single trajectory for given W_coh.

        Returns (x, v) arrays of length n_steps.
        """
        v = np.empty(n_steps, dtype=np.int8)
        x = np.empty(n_steps, dtype=np.float64)

        # random initial direction +/- 1
        v[0] = 1 if rng.random() < 0.5 else -1
        x[0] = 0.0

        p_stay = self.p_stay(wcoh)

        for n in range(1, n_steps):
            if rng.random() < p_stay:
                v[n] = v[n - 1]
            else:
                v[n] = -v[n - 1]
            x[n] = x[n - 1] + v[n - 1]

        return x, v

    @staticmethod
    def acceleration_from_positions(x: np.ndarray) -> np.ndarray:
        """Compute discrete acceleration a_n from positions x_n.

        a_n = x_{n+1} - 2 x_n + x_{n-1}
        Defined for 1 <= n <= N-2; we pad ends with zeros for convenience.
        """
        n = x.shape[0]
        a = np.zeros_like(x)
        if n >= 3:
            a[1:-1] = x[2:] - 2.0 * x[1:-1] + x[:-2]
        return a
