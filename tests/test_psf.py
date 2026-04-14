from __future__ import annotations

import numpy as np

from psf_modeling import compute_psf


def test_compute_psf_is_normalized() -> None:
    pupil = np.ones((64, 64), dtype=float)
    psf = compute_psf(pupil)
    assert np.isclose(psf.sum(), 1.0)


def test_compute_psf_raises_on_empty_pupil() -> None:
    pupil = np.zeros((32, 32), dtype=float)
    try:
        compute_psf(pupil)
    except ValueError:
        pass
    else:
        raise AssertionError("compute_psf should fail on an empty pupil")
