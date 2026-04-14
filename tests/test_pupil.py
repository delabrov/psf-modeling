from __future__ import annotations

import numpy as np

from psf_modeling import add_jwst_spiders, build_hst_pupil, build_jwst_pupil, pupil_circle_obscured


def test_build_jwst_pupil_binary_and_nonempty() -> None:
    pupil = build_jwst_pupil(nx=256)
    uniques = np.unique(pupil)
    assert set(uniques.tolist()).issubset({0.0, 1.0})
    assert pupil.sum() > 0.0


def test_spiders_remove_flux() -> None:
    base = pupil_circle_obscured(256, outer_radius=120, obscuration_radius=25)
    with_spiders = add_jwst_spiders(base, width=6, segment_radius=54)
    assert with_spiders.sum() < base.sum()


def test_build_hst_pupil_has_central_obscuration() -> None:
    pupil = build_hst_pupil(nx=256, outer_radius=60, obscuration_ratio=0.33, spider_width=4)
    cy, cx = 128, 128
    assert pupil[cy, cx] == 0.0
    assert set(np.unique(pupil).tolist()).issubset({0.0, 1.0})
    assert pupil.sum() > 0.0
