#!/usr/bin/env python
"""Build alternative pupils and display their PSFs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from psf_modeling import (
    add_jwst_spiders,
    compute_psf,
    plot_pupil_and_psf,
    pupil_circle,
    pupil_circle_obscured,
    pupil_hexagonal,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nx", type=int, default=512, help="Image size in pixels.")
    parser.add_argument(
        "--pupil",
        choices=["circle", "circle_obscured", "hexagon"],
        default="circle_obscured",
        help="Pupil shape to generate.",
    )
    parser.add_argument("--radius", type=float, default=120.0, help="Main pupil radius (pixels).")
    parser.add_argument(
        "--obscuration-radius",
        type=float,
        default=25.0,
        help="Central obscuration diameter-like parameter used in legacy script.",
    )
    parser.add_argument("--hex-radius", type=float, default=150.0, help="Hexagon radius in pixels.")
    parser.add_argument("--with-spiders", action="store_true", help="Apply JWST-like spider mask.")
    parser.add_argument("--spider-width", type=int, default=6, help="Spider width in pixels.")
    parser.add_argument(
        "--figure-path",
        type=Path,
        default=ROOT / "figures" / "other_pupil_psf.png",
        help="Output path for the generated figure.",
    )
    parser.add_argument(
        "--psf-floor-power",
        type=float,
        default=-8.0,
        help="Lower display floor in log10 for PSF visualization.",
    )
    parser.add_argument(
        "--psf-upper-percentile",
        type=float,
        default=99.9,
        help="Upper percentile used to set PSF display vmax.",
    )
    parser.add_argument(
        "--psf-dynamic-range",
        type=float,
        default=3.0,
        help="Displayed PSF dynamic range in dex below vmax.",
    )
    parser.add_argument("--no-show", action="store_true", help="Do not open a display window.")
    return parser.parse_args()


def build_selected_pupil(args: argparse.Namespace) -> np.ndarray:
    if args.pupil == "circle":
        return pupil_circle(args.nx, args.radius)
    if args.pupil == "hexagon":
        return pupil_hexagonal(args.nx, args.hex_radius)
    return pupil_circle_obscured(args.nx, args.radius, args.obscuration_radius)


def make_titles(args: argparse.Namespace) -> tuple[str, str]:
    if args.pupil == "circle":
        base = "Synthetic Circular"
    elif args.pupil == "hexagon":
        base = "Synthetic Hexagonal"
    else:
        base = "Synthetic Obscured Circular"

    if args.with_spiders or args.pupil == "circle_obscured":
        suffix = " (JWST-like spiders)"
    else:
        suffix = ""

    return f"{base} Pupil{suffix}", f"{base} PSF{suffix}"


def main() -> None:
    args = parse_args()

    pupil = build_selected_pupil(args)
    if args.with_spiders or args.pupil == "circle_obscured":
        pupil = add_jwst_spiders(pupil, width=args.spider_width, segment_radius=54.0)

    psf = compute_psf(pupil)
    x = np.arange(args.nx) - args.nx // 2
    pupil_title, psf_title = make_titles(args)

    plot_pupil_and_psf(
        pupil=pupil,
        psf=psf,
        coords=x,
        pupil_title=pupil_title,
        psf_title=psf_title,
        psf_cmap="gray",
        psf_floor_power=args.psf_floor_power,
        psf_upper_percentile=args.psf_upper_percentile,
        psf_dynamic_range=args.psf_dynamic_range,
        output_path=args.figure_path,
        show=not args.no_show,
    )


if __name__ == "__main__":
    main()
