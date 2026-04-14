#!/usr/bin/env python
"""Apply JWST/HST/other PSFs to a synthetic scene and render observed images."""

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
    add_jwst_spiders,
    build_hst_pupil,
    build_jwst_pupil,
    compute_psf,
    find_brightest_sources,
    generate_synthetic_scene,
    plot_convolved_scenes,
    plot_psf_spike_zooms,
    pupil_circle_obscured,
    save_observation,
    save_scene,
)
from psf_modeling.observation import convolve_scene_with_psf


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
        "--n-galaxies",
        type=int,
        default=0,
        help="Number of extended sources if scene is generated.",
    )
    parser.add_argument(
        "--n-diffuse",
        type=int,
        default=0,
        help="Number of diffuse components if scene is generated.",
    )
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
        "--figure-path",
        type=Path,
        default=ROOT / "figures" / "observed_fields_psf_comparison.png",
        help="Output comparison figure path.",
    )
    parser.add_argument(
        "--zoom-figure-path",
        type=Path,
        default=ROOT / "figures" / "observed_fields_psf_spike_zooms.png",
        help="Output figure path for bright-star PSF zooms.",
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
        default=4.5,
        help="Displayed log dynamic range (dex).",
    )
    parser.add_argument(
        "--n-zoom-stars",
        type=int,
        default=3,
        help="Number of bright stars used for zoom panels.",
    )
    parser.add_argument(
        "--zoom-size",
        type=int,
        default=96,
        help="Cutout size for star zoom panels.",
    )
    parser.add_argument(
        "--output-jwst",
        type=Path,
        default=ROOT / "observed_scene_jwst.npy",
        help="Output path for JWST-convolved scene.",
    )
    parser.add_argument(
        "--output-hst",
        type=Path,
        default=ROOT / "observed_scene_hst.npy",
        help="Output path for HST-convolved scene.",
    )
    parser.add_argument(
        "--output-other",
        type=Path,
        default=ROOT / "observed_scene_other.npy",
        help="Output path for the third PSF-convolved scene.",
    )
    parser.add_argument("--no-show", action="store_true", help="Do not open a display window.")
    return parser.parse_args()


def load_or_generate_scene(
    path: Path,
    nx: int,
    seed: int,
    n_stars: int,
    n_galaxies: int,
    n_diffuse: int,
    regenerate_scene: bool,
):
    if path.exists() and not regenerate_scene:
        return np.load(path)

    scene = generate_synthetic_scene(
        nx=nx,
        seed=seed,
        n_stars=n_stars,
        n_galaxies=n_galaxies,
        n_diffuse=n_diffuse,
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
        n_galaxies=args.n_galaxies,
        n_diffuse=args.n_diffuse,
        regenerate_scene=args.regenerate_scene,
    )

    if scene.ndim != 2 or scene.shape[0] != scene.shape[1]:
        raise ValueError("Current workflow expects a square 2D scene (e.g., 512x512).")

    nx = scene.shape[1]

    # Build PSFs currently used in the project.
    psf_jwst = compute_psf(build_jwst_pupil(nx=nx))
    psf_hst = compute_psf(build_hst_pupil(nx=nx))

    other_pupil = pupil_circle_obscured(nx, outer_radius=120.0, obscuration_radius=25.0)
    other_pupil = add_jwst_spiders(other_pupil, width=6, segment_radius=54.0)
    psf_other = compute_psf(other_pupil)

    obs_jwst = convolve_scene_with_psf(scene, psf_jwst)
    obs_hst = convolve_scene_with_psf(scene, psf_hst)
    obs_other = convolve_scene_with_psf(scene, psf_other)

    save_observation(args.output_jwst, obs_jwst)
    save_observation(args.output_hst, obs_hst)
    save_observation(args.output_other, obs_other)

    plot_convolved_scenes(
        original=scene,
        jwst=obs_jwst,
        hst=obs_hst,
        other=obs_other,
        output_path=args.figure_path,
        show=not args.no_show,
        log_upper_percentile=args.log_upper_percentile,
        log_dynamic_range=args.log_dynamic_range,
    )

    star_positions = find_brightest_sources(
        scene,
        n_sources=args.n_zoom_stars,
        min_separation=max(24, args.zoom_size // 2),
        edge_margin=max(24, args.zoom_size // 2),
    )
    plot_psf_spike_zooms(
        jwst=obs_jwst,
        hst=obs_hst,
        other=obs_other,
        positions=star_positions,
        cutout_size=args.zoom_size,
        output_path=args.zoom_figure_path,
        show=not args.no_show,
        log_upper_percentile=args.log_upper_percentile,
        log_dynamic_range=args.log_dynamic_range,
    )

    print(f"Comparison figure saved to {args.figure_path}")
    print(f"PSF zoom figure saved to {args.zoom_figure_path}")
    print(f"JWST observation saved to {args.output_jwst}")
    print(f"HST observation saved to {args.output_hst}")
    print(f"Other observation saved to {args.output_other}")


if __name__ == "__main__":
    main()
