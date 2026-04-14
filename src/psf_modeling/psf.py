"""PSF computation utilities."""

from __future__ import annotations

import numpy as np


def compute_psf(pupil: np.ndarray) -> np.ndarray:
    """Compute a normalized intensity PSF from a pupil function."""
    field = np.fft.fftshift(np.fft.fft2(pupil))
    intensity = np.abs(field) ** 2
    total_flux = float(np.sum(intensity))
    if total_flux <= 0:
        raise ValueError("Pupil produced zero total flux; cannot normalize PSF.")
    return intensity / total_flux


def log10_psf(psf: np.ndarray, floor_power: float = -12.0) -> np.ndarray:
    """Return log10 PSF with a numerical floor to avoid -inf."""
    floor = 10.0 ** floor_power
    return np.log10(np.clip(psf, floor, None))
