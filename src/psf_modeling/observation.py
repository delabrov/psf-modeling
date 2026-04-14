"""Observation simulation utilities: apply PSFs to synthetic scenes."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def convolve_scene_with_psf(scene: np.ndarray, psf: np.ndarray) -> np.ndarray:
    """Convolve a scene with a centered PSF using same-size FFT convolution.

    The PSF is expected to be centered (peak near image center) and normalized.
    """
    if scene.ndim != 2 or psf.ndim != 2:
        raise ValueError("scene and psf must both be 2D arrays.")

    scene = np.asarray(scene, dtype=float)
    psf = np.asarray(psf, dtype=float)

    if scene.shape != psf.shape:
        raise ValueError("scene and psf must have the same shape for this workflow.")

    if psf.sum() <= 0:
        raise ValueError("PSF must have positive total flux.")

    # PSF is centered in image coordinates; move center to (0,0) for FFT convolution.
    psf_origin = np.fft.ifftshift(psf)
    convolved = np.fft.ifft2(np.fft.fft2(scene) * np.fft.fft2(psf_origin)).real
    return np.clip(convolved, 0.0, None)


def display_stretch(scene: np.ndarray, ref_value: float) -> np.ndarray:
    """Return an asinh stretch normalized to [0, 1] (kept for compatibility)."""
    ref = max(float(ref_value), 1e-12)
    stretched = np.arcsinh(np.clip(scene, 0.0, None) / ref)
    max_val = float(stretched.max())
    if max_val <= 0:
        return stretched
    return stretched / max_val


def _shared_log_images(
    images: list[np.ndarray],
    upper_percentile: float,
    dynamic_range: float,
) -> tuple[list[np.ndarray], float, float]:
    """Convert images to shared log space and return display limits."""
    positive_values = np.concatenate([img[img > 0.0].ravel() for img in images if np.any(img > 0.0)])
    if positive_values.size == 0:
        logs = [np.zeros_like(img) for img in images]
        return logs, -1.0, 0.0

    floor = max(float(np.percentile(positive_values, 0.5)) * 1e-3, 1e-12)
    logs = [np.log10(np.clip(img, floor, None)) for img in images]

    vmax = max(float(np.percentile(log_img, upper_percentile)) for log_img in logs)
    vmin = vmax - float(dynamic_range)
    return logs, vmin, vmax


def plot_convolved_scenes(
    original: np.ndarray,
    jwst: np.ndarray,
    hst: np.ndarray,
    other: np.ndarray,
    output_path: str | Path | None = None,
    show: bool = True,
    log_upper_percentile: float = 99.995,
    log_dynamic_range: float = 4.5,
) -> plt.Figure:
    """Plot original synthetic field and 3 PSF-convolved observations in log scale."""
    images = [original, jwst, hst, other]
    log_images, vmin, vmax = _shared_log_images(
        images,
        upper_percentile=log_upper_percentile,
        dynamic_range=log_dynamic_range,
    )

    fig, axs = plt.subplots(2, 2, figsize=(12, 12))
    axs = axs.ravel()

    items = [
        (log_images[0], "Synthetic Field (No PSF, log scale)"),
        (log_images[1], "Observed Field with Synthetic JWST PSF (log scale)"),
        (log_images[2], "Observed Field with Synthetic HST PSF (log scale)"),
        (log_images[3], "Observed Field with Synthetic Obscured Circular PSF (log scale)"),
    ]

    for ax, (image, title) in zip(axs, items):
        ax.imshow(image, cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
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


def plot_single_observation(
    image: np.ndarray,
    title: str = "Observed Field with Synthetic JWST PSF (log scale)",
    output_path: str | Path | None = None,
    show: bool = True,
    log_upper_percentile: float = 99.995,
    log_dynamic_range: float = 4.5,
) -> plt.Figure:
    """Plot a single observed image using log-scale display."""
    (log_image,), vmin, vmax = _shared_log_images(
        [image],
        upper_percentile=log_upper_percentile,
        dynamic_range=log_dynamic_range,
    )

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.imshow(log_image, cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
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


def plot_scene_vs_jwst_observation(
    scene: np.ndarray,
    jwst_observation: np.ndarray,
    output_path: str | Path | None = None,
    show: bool = True,
    log_upper_percentile: float = 99.995,
    log_dynamic_range: float = 4.8,
) -> plt.Figure:
    """Plot side-by-side original synthetic field and JWST-convolved field."""
    log_images, vmin, vmax = _shared_log_images(
        [scene, jwst_observation],
        upper_percentile=log_upper_percentile,
        dynamic_range=log_dynamic_range,
    )

    fig, axs = plt.subplots(1, 2, figsize=(13, 6))
    items = [
        (log_images[0], "Synthetic Stellar Field (No PSF, log scale)"),
        (log_images[1], "Observed Stellar Field with Synthetic JWST PSF (log scale)"),
    ]

    for ax, (image, title) in zip(axs, items):
        ax.imshow(image, cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
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


def find_brightest_sources(
    scene: np.ndarray,
    n_sources: int = 3,
    min_separation: int = 40,
    edge_margin: int = 48,
) -> list[tuple[int, int]]:
    """Find bright source coordinates with a minimum separation constraint."""
    work = np.array(scene, dtype=float, copy=True)
    ny, nx = work.shape
    yy, xx = np.indices(work.shape)

    positions: list[tuple[int, int]] = []
    for _ in range(max(0, n_sources)):
        idx = int(np.argmax(work))
        y, x = np.unravel_index(idx, work.shape)
        peak = work[y, x]
        if peak <= 0.0:
            break

        if edge_margin <= x < (nx - edge_margin) and edge_margin <= y < (ny - edge_margin):
            positions.append((x, y))

        mask = (xx - x) ** 2 + (yy - y) ** 2 <= min_separation**2
        work[mask] = 0.0

    return positions


def _extract_cutout(image: np.ndarray, x: int, y: int, size: int) -> np.ndarray:
    """Extract a square cutout centered on (x, y)."""
    half = size // 2
    return image[y - half : y + half, x - half : x + half]


def plot_psf_spike_zooms(
    jwst: np.ndarray,
    hst: np.ndarray,
    other: np.ndarray,
    positions: list[tuple[int, int]],
    cutout_size: int = 96,
    output_path: str | Path | None = None,
    show: bool = True,
    log_upper_percentile: float = 99.995,
    log_dynamic_range: float = 4.2,
) -> plt.Figure | None:
    """Plot log-scale zooms on bright stars to make diffraction spikes visible."""
    if not positions:
        return None

    n_rows = len(positions)
    fig, axs = plt.subplots(n_rows, 3, figsize=(12, 4 * n_rows))
    if n_rows == 1:
        axs = np.array([axs])

    cutout_sets: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    for x, y in positions:
        cutout_sets.append(
            (
                _extract_cutout(jwst, x, y, cutout_size),
                _extract_cutout(hst, x, y, cutout_size),
                _extract_cutout(other, x, y, cutout_size),
            )
        )

    all_cutouts = [arr for triplet in cutout_sets for arr in triplet]
    log_cutouts, vmin, vmax = _shared_log_images(
        all_cutouts,
        upper_percentile=log_upper_percentile,
        dynamic_range=log_dynamic_range,
    )

    titles = ["JWST PSF", "HST PSF", "Obscured Circular PSF"]
    k = 0
    for r, (x, y) in enumerate(positions):
        for c in range(3):
            ax = axs[r, c]
            ax.imshow(log_cutouts[k], cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
            k += 1
            if r == 0:
                ax.set_title(titles[c])
            ax.set_xlabel("x [pix]")
            ax.set_ylabel("y [pix]")
        axs[r, 0].text(
            0.02,
            0.95,
            f"star at (x={x}, y={y})",
            transform=axs[r, 0].transAxes,
            va="top",
            ha="left",
            color="white",
            fontsize=9,
            bbox={"facecolor": "black", "alpha": 0.35, "pad": 2},
        )

    fig.suptitle("Bright-Star Zooms (log scale): Diffraction Spikes")
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


def plot_single_psf_spike_zooms(
    image: np.ndarray,
    positions: list[tuple[int, int]],
    cutout_size: int = 96,
    output_path: str | Path | None = None,
    show: bool = True,
    log_upper_percentile: float = 99.995,
    log_dynamic_range: float = 4.2,
    title: str = "JWST PSF",
) -> plt.Figure | None:
    """Plot log-scale zooms on bright stars for a single observed image."""
    if not positions:
        return None

    n_rows = len(positions)
    fig, axs = plt.subplots(n_rows, 1, figsize=(4.4, 4 * n_rows))
    if n_rows == 1:
        axs = np.array([axs])

    cutouts = [_extract_cutout(image, x, y, cutout_size) for x, y in positions]
    log_cutouts, vmin, vmax = _shared_log_images(
        cutouts,
        upper_percentile=log_upper_percentile,
        dynamic_range=log_dynamic_range,
    )

    for i, ((x, y), ax) in enumerate(zip(positions, axs)):
        ax.imshow(log_cutouts[i], cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
        if i == 0:
            ax.set_title(title)
        ax.set_xlabel("x [pix]")
        ax.set_ylabel("y [pix]")
        ax.text(
            0.02,
            0.95,
            f"star at (x={x}, y={y})",
            transform=ax.transAxes,
            va="top",
            ha="left",
            color="white",
            fontsize=9,
            bbox={"facecolor": "black", "alpha": 0.35, "pad": 2},
        )

    fig.suptitle("Bright-Star Zooms (log scale): Diffraction Spikes")
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


def save_observation(path: str | Path, observation: np.ndarray) -> None:
    """Save convolved observation as .npy or text depending on extension."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".npy":
        np.save(path, observation)
    else:
        np.savetxt(path, observation)
