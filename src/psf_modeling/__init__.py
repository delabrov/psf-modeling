"""Utilities to model telescope pupils and PSFs."""

from .plotting import plot_pupil_and_psf
from .psf import compute_psf, log10_psf
from .pupil import (
    add_jwst_spiders,
    build_jwst_pupil,
    load_pupil,
    pupil_circle,
    pupil_circle_obscured,
    pupil_hexagonal,
    save_pupil,
)

__all__ = [
    "add_jwst_spiders",
    "build_jwst_pupil",
    "compute_psf",
    "load_pupil",
    "log10_psf",
    "plot_pupil_and_psf",
    "pupil_circle",
    "pupil_circle_obscured",
    "pupil_hexagonal",
    "save_pupil",
]
