"""Synthetic scene generation utilities (no PSF convolution)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _sample_star_fluxes(
    rng: np.random.Generator,
    n_stars: int,
    flux_range: tuple[float, float],
    bright_tail_fraction: float = 0.06,
) -> np.ndarray:
    """Sample stellar fluxes with a broad, realistic heavy-tailed distribution."""
    if n_stars <= 0:
        return np.zeros(0, dtype=float)

    f_min = max(float(flux_range[0]), 1e-9)
    f_max = max(float(flux_range[1]), f_min * 10.0)

    # Three-population luminosity function in log-flux:
    # many faint stars, some intermediate stars, and a rare bright population.
    log_min = float(np.log10(f_min))
    log_max = float(np.log10(f_max))
    span = max(log_max - log_min, 1e-6)
    break_1 = log_min + 0.45 * span
    break_2 = log_min + 0.80 * span

    counts = rng.multinomial(n_stars, [0.80, 0.16, 0.04])
    low = 10.0 ** rng.uniform(log_min, break_1, counts[0])
    mid = 10.0 ** rng.uniform(break_1, break_2, counts[1])
    high = 10.0 ** rng.uniform(break_2, log_max, counts[2])
    fluxes = np.concatenate([low, mid, high])
    rng.shuffle(fluxes)

    # Add a bright-end boost to a tiny subset to emulate very bright stars.
    n_tail = int(round(n_stars * max(0.0, min(bright_tail_fraction, 0.5))))
    if n_tail > 0:
        tail_idx = rng.choice(n_stars, size=n_tail, replace=False)
        boost = 10.0 ** rng.uniform(0.5, 1.2, size=n_tail)  # x3 to x16
        fluxes[tail_idx] *= boost

    return np.clip(fluxes, f_min, f_max)


def _add_subpixel_point(image: np.ndarray, x: float, y: float, flux: float) -> None:
    """Deposit a point source using bilinear weights."""
    ny, nx = image.shape
    ix = int(np.floor(x))
    iy = int(np.floor(y))

    if ix < 0 or ix >= nx - 1 or iy < 0 or iy >= ny - 1:
        return

    dx = x - ix
    dy = y - iy

    image[iy, ix] += flux * (1.0 - dx) * (1.0 - dy)
    image[iy, ix + 1] += flux * dx * (1.0 - dy)
    image[iy + 1, ix] += flux * (1.0 - dx) * dy
    image[iy + 1, ix + 1] += flux * dx * dy


def _elliptical_radius(xx: np.ndarray, yy: np.ndarray, cx: float, cy: float, q: float, theta: float) -> np.ndarray:
    """Return elliptical radius after rotation by theta (radians)."""
    c = np.cos(theta)
    s = np.sin(theta)
    dx = xx - cx
    dy = yy - cy
    xp = dx * c + dy * s
    yp = -dx * s + dy * c
    return np.sqrt(xp**2 + (yp / max(q, 1e-3)) ** 2)


def _add_sersic_blob(
    image: np.ndarray,
    cx: float,
    cy: float,
    flux: float,
    re: float,
    n: float,
    q: float,
    theta: float,
) -> None:
    """Add a compact/extended galaxy-like source with a simplified Sersic profile."""
    ny, nx = image.shape
    radius = int(max(8.0, 6.0 * re))
    x_min = max(0, int(np.floor(cx - radius)))
    x_max = min(nx, int(np.ceil(cx + radius + 1)))
    y_min = max(0, int(np.floor(cy - radius)))
    y_max = min(ny, int(np.ceil(cy + radius + 1)))

    if x_min >= x_max or y_min >= y_max:
        return

    yy, xx = np.indices((y_max - y_min, x_max - x_min), dtype=float)
    xx += x_min
    yy += y_min

    r = _elliptical_radius(xx, yy, cx, cy, q=q, theta=theta)
    profile = np.exp(-((r / max(re, 1e-3)) ** (1.0 / max(n, 1e-3))))

    norm = float(profile.sum())
    if norm <= 0:
        return

    image[y_min:y_max, x_min:x_max] += flux * profile / norm


def _add_diffuse_component(
    image: np.ndarray,
    cx: float,
    cy: float,
    flux: float,
    sigma_x: float,
    sigma_y: float,
    theta: float,
) -> None:
    """Add a broad diffuse Gaussian-like emission component."""
    ny, nx = image.shape
    yy, xx = np.indices((ny, nx), dtype=float)

    c = np.cos(theta)
    s = np.sin(theta)
    dx = xx - cx
    dy = yy - cy
    xp = dx * c + dy * s
    yp = -dx * s + dy * c

    profile = np.exp(-0.5 * ((xp / max(sigma_x, 1e-3)) ** 2 + (yp / max(sigma_y, 1e-3)) ** 2))
    norm = float(profile.sum())
    if norm <= 0:
        return

    image += flux * profile / norm


def generate_synthetic_scene(
    nx: int = 512,
    ny: int | None = None,
    n_stars: int = 120,
    n_galaxies: int = 0,
    n_diffuse: int = 0,
    star_flux_range: tuple[float, float] = (3.0, 1_000_000.0),
    galaxy_flux_range: tuple[float, float] = (900.0, 35000.0),
    diffuse_flux_range: tuple[float, float] = (8e4, 3.5e5),
    seed: int = 42,
) -> np.ndarray:
    """Generate a synthetic wide field with stars, galaxies, and diffuse sources.

    This function returns a clean sky scene before any PSF convolution.
    """
    if ny is None:
        ny = nx

    rng = np.random.default_rng(seed)
    scene = np.zeros((ny, nx), dtype=float)

    # Point sources (stars): broad luminosity function (many faint, few bright).
    star_fluxes = _sample_star_fluxes(rng, n_stars=n_stars, flux_range=star_flux_range)
    for flux in star_fluxes:
        x = rng.uniform(2.0, nx - 3.0)
        y = rng.uniform(2.0, ny - 3.0)
        _add_subpixel_point(scene, x, y, float(flux))

    # Extended sources (galaxies)
    galaxy_fluxes = 10.0 ** rng.uniform(
        np.log10(galaxy_flux_range[0]), np.log10(galaxy_flux_range[1]), n_galaxies
    )
    for flux in galaxy_fluxes:
        cx = rng.uniform(10.0, nx - 11.0)
        cy = rng.uniform(10.0, ny - 11.0)
        re = rng.uniform(2.5, 10.0)
        n = rng.uniform(0.8, 3.5)
        q = rng.uniform(0.35, 1.0)
        theta = rng.uniform(0.0, np.pi)
        _add_sersic_blob(scene, cx, cy, float(flux), re, n, q, theta)

    # Diffuse emission (nebula-like large components)
    diffuse_fluxes = 10.0 ** rng.uniform(
        np.log10(diffuse_flux_range[0]), np.log10(diffuse_flux_range[1]), n_diffuse
    )
    for flux in diffuse_fluxes:
        cx = rng.uniform(0.0, nx - 1.0)
        cy = rng.uniform(0.0, ny - 1.0)
        sigma_x = rng.uniform(40.0, 120.0)
        sigma_y = rng.uniform(20.0, 80.0)
        theta = rng.uniform(0.0, np.pi)
        _add_diffuse_component(scene, cx, cy, float(flux), sigma_x, sigma_y, theta)

    # Add a mild smooth sky background and keep positivity.
    scene += np.percentile(scene, 5) * 0.05
    return np.clip(scene, 0.0, None)


def scene_for_display(scene: np.ndarray, stretch_percentile: float = 99.9) -> np.ndarray:
    """Return an asinh-stretched scene for visualization."""
    if np.all(scene <= 0):
        return np.zeros_like(scene)

    ref = float(np.percentile(scene, stretch_percentile))
    ref = max(ref, 1e-12)
    scaled = np.arcsinh(scene / ref)
    max_scaled = float(np.max(scaled))
    if max_scaled <= 0:
        return scaled
    return scaled / max_scaled


def plot_synthetic_scene(
    scene: np.ndarray,
    title: str = "Synthetic Wide Field (Before PSF Convolution)",
    cmap: str = "gray",
    output_path: str | Path | None = None,
    show: bool = True,
) -> plt.Figure:
    """Plot a synthetic field image."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.imshow(scene_for_display(scene), cmap=cmap, origin="lower")
    ax.set_title(title)
    ax.set_xlabel("x [pixels]")
    ax.set_ylabel("y [pixels]")
    fig.tight_layout()

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=180, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig


def save_scene(path: str | Path, scene: np.ndarray) -> None:
    """Save synthetic scene as .npy or text depending on extension."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".npy":
        np.save(path, scene)
    else:
        np.savetxt(path, scene)
