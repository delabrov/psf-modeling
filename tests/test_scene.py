from __future__ import annotations

import numpy as np

from psf_modeling import generate_synthetic_scene


def test_generate_synthetic_scene_shape_and_positivity() -> None:
    scene = generate_synthetic_scene(nx=128, ny=96, n_stars=10, n_galaxies=5, n_diffuse=2, seed=0)
    assert scene.shape == (96, 128)
    assert np.all(scene >= 0.0)


def test_generate_synthetic_scene_reproducible_with_seed() -> None:
    scene_1 = generate_synthetic_scene(nx=128, n_stars=20, n_galaxies=8, n_diffuse=3, seed=7)
    scene_2 = generate_synthetic_scene(nx=128, n_stars=20, n_galaxies=8, n_diffuse=3, seed=7)
    assert np.allclose(scene_1, scene_2)


def test_generate_synthetic_scene_contains_bright_sources() -> None:
    scene = generate_synthetic_scene(nx=128, n_stars=20, n_galaxies=8, n_diffuse=3, seed=11)
    p99 = float(np.percentile(scene, 99))
    p50 = float(np.percentile(scene, 50))
    assert p99 > p50
