"""Plot helpers for pupil / PSF visualization."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .psf import log10_psf


def plot_pupil_and_psf(
    pupil: np.ndarray,
    psf: np.ndarray,
    coords: np.ndarray | None = None,
    pupil_title: str = "Pupil",
    psf_title: str = "PSF",
    psf_cmap: str = "gray",
    figure_title: str | None = None,
    output_path: str | Path | None = None,
    show: bool = True,
) -> tuple[plt.Figure, np.ndarray]:
    """Plot a pupil image and its log-scaled PSF side by side."""
    if coords is None:
        nx = pupil.shape[0]
        coords = np.arange(nx) - nx // 2

    fig, axs = plt.subplots(1, 2, figsize=(10, 5.5))

    axs[0].imshow(pupil, cmap="gray")
    axs[0].set_title(pupil_title)
    axs[0].set_aspect("equal", "box")

    axs[1].pcolormesh(coords, coords, log10_psf(psf), cmap=psf_cmap, shading="auto")
    axs[1].set_title(psf_title)
    axs[1].set_aspect("equal", "box")

    if figure_title:
        fig.suptitle(figure_title)

    fig.tight_layout()

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=180, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig, axs
