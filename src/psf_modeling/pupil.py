"""Pupil generation utilities for Fourier optics PSF simulations."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def centered_coordinates(nx: int) -> np.ndarray:
    """Return centered pixel coordinates in the range [-nx/2, nx/2)."""
    return np.arange(nx) - nx // 2


def regular_hexagon_mask(
    xx: np.ndarray,
    yy: np.ndarray,
    center: tuple[float, float],
    radius: float,
) -> np.ndarray:
    """Return a flat-top regular hexagon mask centered on ``center``.

    The radius is the distance from center to a vertex.
    """
    cx, cy = center
    dx = xx - cx
    dy = yy - cy
    sqrt3 = np.sqrt(3.0)

    return (
        (np.abs(dx) <= radius)
        & (np.abs(dy) <= sqrt3 * radius / 2.0)
        & (sqrt3 * np.abs(dx) + np.abs(dy) <= sqrt3 * radius)
    )


def jwst_segment_centers(radius: float, gap: float = 2.0) -> list[tuple[float, float]]:
    """Return segment centers for a simplified 18-segment JWST primary mirror."""
    r_hexa = np.sqrt(3.0) * radius / 2.0
    a = np.sqrt((2 * r_hexa + gap) ** 2 - (r_hexa + gap) ** 2)
    b = np.sqrt((4 * r_hexa + 2 * gap) ** 2 - (2 * r_hexa + gap) ** 2)

    return [
        (0, 2 * r_hexa + gap),
        (0, 4 * r_hexa + 2 * gap),
        (0, -(2 * r_hexa + gap)),
        (0, -(4 * r_hexa + 2 * gap)),
        (a, r_hexa + gap),
        (a, -(r_hexa + gap)),
        (-a, r_hexa + gap),
        (-a, -(r_hexa + gap)),
        (a, 3 * r_hexa + 2 * gap),
        (a, -(3 * r_hexa + 2 * gap)),
        (-a, 3 * r_hexa + 2 * gap),
        (-a, -(3 * r_hexa + 2 * gap)),
        (b, 2 * r_hexa + gap),
        (b, -(2 * r_hexa + gap)),
        (-b, 2 * r_hexa + gap),
        (-b, -(2 * r_hexa + gap)),
        (b, 0),
        (-b, 0),
    ]


def add_jwst_spiders(
    pupil: np.ndarray,
    width: int = 6,
    segment_radius: float = 54.0,
) -> np.ndarray:
    """Add a simplified 3-arm JWST spider pattern (legacy orientation).

    This mirrors the geometry used in the original project script.
    """
    new_pupil = np.array(pupil, dtype=float, copy=True)
    nx = new_pupil.shape[0]

    ii, jj = np.indices(new_pupil.shape)
    tan30 = np.tan(np.deg2rad(30.0))

    vertical = (ii >= nx // 2) & (np.abs(jj - nx // 2) <= width // 2)

    x_max_1 = ii * tan30 + (2 * segment_radius + (width + 2) / 2)
    x_min_1 = ii * tan30 + (2 * segment_radius - (width + 2) / 2)
    diag_1 = (ii < nx // 2) & (jj <= x_max_1) & (jj >= x_min_1)

    x_min_2 = (-ii * tan30 - (2 * segment_radius + (width + 2) / 2)).astype(int) + nx
    x_max_2 = (-ii * tan30 - (2 * segment_radius - (width + 2) / 2)).astype(int) + nx
    diag_2 = (ii < nx // 2) & (jj >= x_min_2) & (jj <= x_max_2)

    new_pupil[vertical | diag_1 | diag_2] = 0.0
    return new_pupil


def build_jwst_pupil(
    nx: int = 512,
    segment_radius: float = 54.0,
    segment_gap: float = 2.0,
    spider_width: int = 6,
) -> np.ndarray:
    """Build a simplified binary JWST pupil (segments + spiders)."""
    coords = centered_coordinates(nx)
    xx, yy = np.meshgrid(coords, -coords)

    mask = np.zeros((nx, nx), dtype=bool)
    for center in jwst_segment_centers(segment_radius, segment_gap):
        mask |= regular_hexagon_mask(xx, yy, center, segment_radius)

    pupil = mask.astype(float)
    return add_jwst_spiders(pupil, width=spider_width, segment_radius=segment_radius)


def add_hst_spiders(pupil: np.ndarray, width: int = 4) -> np.ndarray:
    """Add a simplified HST 4-spike support pattern (orthogonal spiders)."""
    new_pupil = np.array(pupil, dtype=float, copy=True)
    ny, nx = new_pupil.shape
    cy, cx = ny // 2, nx // 2
    ii, jj = np.indices(new_pupil.shape)

    spider_mask = (np.abs(ii - cy) <= width // 2) | (np.abs(jj - cx) <= width // 2)
    new_pupil[spider_mask] = 0.0
    return new_pupil


def build_hst_pupil(
    nx: int = 512,
    outer_radius: float = 120.0,
    obscuration_ratio: float = 0.33,
    spider_width: int = 4,
) -> np.ndarray:
    """Build a simplified HST-like binary pupil (obscured circle + spiders)."""
    if not (0.0 < obscuration_ratio < 1.0):
        raise ValueError("obscuration_ratio must be between 0 and 1.")

    coords = centered_coordinates(nx)
    xx, yy = np.meshgrid(coords, coords)
    rr = np.sqrt(xx**2 + yy**2)

    obscuration_radius = outer_radius * obscuration_ratio
    pupil = ((rr < outer_radius) & (rr > obscuration_radius)).astype(float)
    return add_hst_spiders(pupil, width=spider_width)


def pupil_circle(nx: int, radius: float) -> np.ndarray:
    """Binary circular pupil."""
    coords = centered_coordinates(nx)
    xx, yy = np.meshgrid(coords, coords)
    return (np.sqrt(xx**2 + yy**2) < radius).astype(float)


def pupil_circle_obscured(nx: int, outer_radius: float, obscuration_radius: float) -> np.ndarray:
    """Binary circular pupil with central obscuration."""
    coords = centered_coordinates(nx)
    xx, yy = np.meshgrid(coords, coords)
    rr = np.sqrt(xx**2 + yy**2)
    return ((rr < outer_radius / 2.0) & (rr > obscuration_radius / 2.0)).astype(float)


def pupil_hexagonal(nx: int, radius: float) -> np.ndarray:
    """Single centered hexagonal pupil."""
    coords = centered_coordinates(nx)
    xx, yy = np.meshgrid(coords, -coords)
    return regular_hexagon_mask(xx, yy, (0.0, 0.0), radius).astype(float)


def save_pupil(path: str | Path, pupil: np.ndarray) -> None:
    """Save a pupil as .npy or text depending on extension."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".npy":
        np.save(path, pupil)
    else:
        np.savetxt(path, pupil, fmt="%.0f")


def load_pupil(path: str | Path) -> np.ndarray:
    """Load a pupil from .npy or text."""
    path = Path(path)
    if path.suffix == ".npy":
        return np.load(path)
    return np.loadtxt(path)
