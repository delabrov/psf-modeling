"""Utilities to model telescope pupils and PSFs."""

from .plotting import plot_pupil_and_psf
from .psf import compute_psf, log10_psf
from .observation import convolve_scene_with_psf, display_stretch, plot_convolved_scenes, save_observation
from .observation import find_brightest_sources, plot_psf_spike_zooms, plot_single_observation
from .observation import plot_scene_vs_jwst_observation, plot_single_psf_spike_zooms
from .pupil import (
    add_hst_spiders,
    add_jwst_spiders,
    build_hst_pupil,
    build_jwst_pupil,
    load_pupil,
    pupil_circle,
    pupil_circle_obscured,
    pupil_hexagonal,
    save_pupil,
)
from .scene import generate_synthetic_scene, plot_synthetic_scene, save_scene, scene_for_display

__all__ = [
    "add_hst_spiders",
    "add_jwst_spiders",
    "build_hst_pupil",
    "build_jwst_pupil",
    "compute_psf",
    "convolve_scene_with_psf",
    "display_stretch",
    "find_brightest_sources",
    "load_pupil",
    "log10_psf",
    "plot_convolved_scenes",
    "plot_psf_spike_zooms",
    "plot_scene_vs_jwst_observation",
    "plot_single_psf_spike_zooms",
    "plot_single_observation",
    "plot_pupil_and_psf",
    "plot_synthetic_scene",
    "pupil_circle",
    "pupil_circle_obscured",
    "pupil_hexagonal",
    "save_observation",
    "save_pupil",
    "save_scene",
    "scene_for_display",
    "generate_synthetic_scene",
]
