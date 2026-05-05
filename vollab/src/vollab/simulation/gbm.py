"""Geometric Brownian Motion path simulation.

dS_t = μ S_t dt + σ S_t dW_t

Discretized: S_{t+Δt} = S_t exp[(μ - σ²/2)Δt + σ√Δt Z_t]
"""

from __future__ import annotations

import numpy as np


def simulate_gbm(
    S0: float,
    mu: float,
    sigma: float,
    T: float,
    n_steps: int = 252,
    n_paths: int = 10_000,
    seed: int = 42,
) -> np.ndarray:
    """Return (n_paths, n_steps+1) array of simulated price paths."""
    rng = np.random.default_rng(seed)
    dt = T / n_steps
    drift = (mu - 0.5 * sigma**2) * dt
    diffusion = sigma * np.sqrt(dt)

    Z = rng.standard_normal((n_paths, n_steps))
    log_returns = drift + diffusion * Z
    log_paths = np.cumsum(log_returns, axis=1)
    log_paths = np.insert(log_paths, 0, 0.0, axis=1)

    return S0 * np.exp(log_paths)
