#!/usr/bin/env python
"""Apply only the JWST PSF to a synthetic scene and render JWST-only figures."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from psf_modeling import (
    build_jwst_pupil,
    compute_psf,
    convolve_scene_with_psf,
    generate_synthetic_scene,
    plot_scene_vs_jwst_observation,
    plot_single_psf_spike_zooms,
    plot_single_observation,
    save_observation,
    save_scene,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scene-path",
        type=Path,
        default=ROOT / "synthetic_scene.npy",
        help="Path to input synthetic scene (.npy).",
    )
    parser.add_argument("--nx", type=int, default=512, help="Scene size used only if scene is generated.")
    parser.add_argument("--n-stars", type=int, default=120, help="Number of point sources if scene is generated.")
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used only if scene is generated.",
    )
    parser.add_argument(
        "--regenerate-scene",
        action="store_true",
        help="Regenerate scene even if --scene-path already exists.",
    )
    parser.add_argument(
        "--jwst-figure-path",
        type=Path,
        default=ROOT / "figures" / "observed_field_jwst_only.png",
        help="Output figure path for the JWST-only observed field.",
    )
    parser.add_argument(
        "--jwst-side-by-side-path",
        type=Path,
        default=ROOT / "figures" / "observed_field_initial_vs_jwst.png",
        help="Output figure path for initial field vs JWST-convolved field.",
    )
    parser.add_argument(
        "--jwst-zoom-figure-path",
        type=Path,
        default=ROOT / "figures" / "observed_field_jwst_star_zoom.png",
        help="Output figure path for a single JWST star zoom.",
    )
    parser.add_argument(
        "--output-jwst",
        type=Path,
        default=ROOT / "observed_scene_jwst.npy",
        help="Output path for JWST-convolved scene.",
    )
    parser.add_argument(
        "--log-upper-percentile",
        type=float,
        default=99.995,
        help="Upper percentile for log-scale display clipping.",
    )
    parser.add_argument(
        "--log-dynamic-range",
        type=float,
        default=4.8,
        help="Displayed log dynamic range (dex) for JWST rendering.",
    )
    parser.add_argument("--zoom-x", type=int, default=421, help="x pixel coordinate for single-star zoom.")
    parser.add_argument("--zoom-y", type=int, default=436, help="y pixel coordinate for single-star zoom.")
    parser.add_argument(
        "--zoom-size",
        type=int,
        default=96,
        help="Cutout size for the single-star zoom panel.",
    )
    parser.add_argument("--no-show", action="store_true", help="Do not open a display window.")
    return parser.parse_args()


def load_or_generate_scene(path: Path, nx: int, seed: int, n_stars: int, regenerate_scene: bool) -> np.ndarray:
    if path.exists() and not regenerate_scene:
        return np.load(path)

    scene = generate_synthetic_scene(
        nx=nx,
        seed=seed,
        n_stars=n_stars,
        n_galaxies=0,
        n_diffuse=0,
    )
    save_scene(path, scene)
    return scene


def main() -> None:
    args = parse_args()

    scene = load_or_generate_scene(
        args.scene_path,
        nx=args.nx,
        seed=args.seed,
        n_stars=args.n_stars,
        regenerate_scene=args.regenerate_scene,
    )

    if scene.ndim != 2 or scene.shape[0] != scene.shape[1]:
        raise ValueError("Current workflow expects a square 2D scene (e.g., 512x512).")

    nx = scene.shape[1]

    psf_jwst = compute_psf(build_jwst_pupil(nx=nx))
    obs_jwst = convolve_scene_with_psf(scene, psf_jwst)
    save_observation(args.output_jwst, obs_jwst)

    plot_single_observation(
        obs_jwst,
        title="Observed Field with Synthetic JWST PSF (log scale)",
        output_path=args.jwst_figure_path,
        show=not args.no_show,
        log_upper_percentile=args.log_upper_percentile,
        log_dynamic_range=args.log_dynamic_range,
    )

    plot_scene_vs_jwst_observation(
        scene=scene,
        jwst_observation=obs_jwst,
        output_path=args.jwst_side_by_side_path,
        show=not args.no_show,
        log_upper_percentile=args.log_upper_percentile,
        log_dynamic_range=args.log_dynamic_range,
    )

    half = args.zoom_size // 2
    x, y = args.zoom_x, args.zoom_y
    ny, nx = obs_jwst.shape
    if x - half < 0 or x + half > nx or y - half < 0 or y + half > ny:
        raise ValueError(
            f"Requested zoom position (x={x}, y={y}) with size={args.zoom_size} is out of bounds for "
            f"image shape ({ny}, {nx})."
        )

    plot_single_psf_spike_zooms(
        image=obs_jwst,
        positions=[(x, y)],
        cutout_size=args.zoom_size,
        output_path=args.jwst_zoom_figure_path,
        show=not args.no_show,
        log_upper_percentile=args.log_upper_percentile,
        log_dynamic_range=args.log_dynamic_range,
        title="JWST PSF (single-star zoom)",
    )

    print(f"JWST-only figure saved to {args.jwst_figure_path}")
    print(f"Initial vs JWST figure saved to {args.jwst_side_by_side_path}")
    print(f"JWST zoom figure saved to {args.jwst_zoom_figure_path}")
    print(f"JWST observation saved to {args.output_jwst}")


if __name__ == "__main__":
    main()
