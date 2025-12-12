from __future__ import annotations

import numpy as np


def estimate_psd(a: np.ndarray, dt: float) -> tuple[np.ndarray, np.ndarray]:
    """Estimate one-sided PSD S_a(omega) for a time series a_n.

    Uses a Hann window and an FFT-based estimator. The normalisation is chosen
    so that the integral over angular frequency approximates the variance.
    """
    a = np.asarray(a, dtype=float)
    n = a.size
    if n < 4:
        raise ValueError("Time series too short for PSD estimation")

    window = np.hanning(n)
    a_win = a * window
    # real FFT
    A = np.fft.rfft(a_win)
    freqs = np.fft.rfftfreq(n, d=dt)  # in Hz
    omega = 2.0 * np.pi * freqs       # angular frequency

    # normalisation: see e.g. standard periodogram; include factor 2 for one-sided
    scale = (dt**2) / (np.sum(window**2) * n)
    S = 2.0 * scale * (A.conj() * A).real

    return omega, S


def amplitude_and_omega_c(omega: np.ndarray, S: np.ndarray) -> tuple[float, float]:
    """Compute overall amplitude A and spectral centroid omega_c.

    A^2 = integral S(omega) d omega
    omega_c = (integral omega S d omega) / (integral S d omega)
    """
    omega = np.asarray(omega, dtype=float)
    S = np.asarray(S, dtype=float)
    if omega.size != S.size:
        raise ValueError("omega and S must have same length")

    if omega.size < 2:
        return 0.0, 0.0

    # simple trapezoidal integration
    total_power = np.trapz(S, omega)
    A = float(np.sqrt(max(total_power, 0.0)))

    if total_power > 0.0:
        omega_c = float(np.trapz(omega * S, omega) / total_power)
    else:
        omega_c = 0.0

    return A, omega_c
