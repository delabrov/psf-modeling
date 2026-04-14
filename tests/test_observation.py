from __future__ import annotations

import numpy as np

from psf_modeling import convolve_scene_with_psf, find_brightest_sources


def test_convolution_preserves_shape() -> None:
    scene = np.zeros((64, 64), dtype=float)
    scene[32, 32] = 1.0
    psf = np.zeros((64, 64), dtype=float)
    psf[32, 32] = 1.0
    out = convolve_scene_with_psf(scene, psf)
    assert out.shape == scene.shape


def test_convolution_preserves_total_flux_with_normalized_psf() -> None:
    rng = np.random.default_rng(0)
    scene = rng.random((64, 64))

    psf = np.zeros((64, 64), dtype=float)
    psf[32, 32] = 0.6
    psf[31, 32] = 0.2
    psf[33, 32] = 0.2
    psf /= psf.sum()

    out = convolve_scene_with_psf(scene, psf)
    assert np.isclose(out.sum(), scene.sum(), rtol=1e-10, atol=1e-10)


def test_convolution_of_centered_delta_recovers_psf() -> None:
    n = 64
    scene = np.zeros((n, n), dtype=float)
    scene[n // 2, n // 2] = 1.0

    psf = np.zeros((n, n), dtype=float)
    psf[n // 2, n // 2] = 0.6
    psf[n // 2 - 1, n // 2] = 0.2
    psf[n // 2 + 1, n // 2] = 0.2
    psf /= psf.sum()

    out = convolve_scene_with_psf(scene, psf)
    assert np.allclose(out, psf, atol=1e-12)


def test_find_brightest_sources_detects_peaks() -> None:
    scene = np.zeros((64, 64), dtype=float)
    scene[10, 10] = 5.0
    scene[30, 30] = 8.0
    scene[50, 50] = 6.0

    positions = find_brightest_sources(scene, n_sources=3, min_separation=8, edge_margin=4)
    assert len(positions) == 3
