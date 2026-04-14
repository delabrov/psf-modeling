#!/usr/bin/env python
"""Generate a simplified HST pupil, compute its PSF, and plot both."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from psf_modeling import build_hst_pupil, compute_psf, plot_pupil_and_psf, save_pupil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nx", type=int, default=512, help="Image size in pixels.")
    parser.add_argument("--outer-radius", type=float, default=120.0, help="Primary mirror radius in pixels.")
    parser.add_argument(
        "--obscuration-ratio",
        type=float,
        default=0.33,
        help="Secondary mirror radius ratio with respect to primary radius.",
    )
    parser.add_argument("--spider-width", type=int, default=4, help="Spider width in pixels.")
    parser.add_argument(
        "--output-pupil-dat",
        type=Path,
        default=ROOT / "pupil_HST.dat",
        help="Path to save the pupil text map.",
    )
    parser.add_argument(
        "--figure-path",
        type=Path,
        default=ROOT / "figures" / "hst_pupil_psf.png",
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


def main() -> None:
    args = parse_args()

    pupil_hst = build_hst_pupil(
        nx=args.nx,
        outer_radius=args.outer_radius,
        obscuration_ratio=args.obscuration_ratio,
        spider_width=args.spider_width,
    )
    psf_hst = compute_psf(pupil_hst)

    save_pupil(args.output_pupil_dat, pupil_hst)

    x = np.arange(args.nx) - args.nx // 2
    plot_pupil_and_psf(
        pupil=pupil_hst,
        psf=psf_hst,
        coords=x,
        pupil_title="Synthetic HST Pupil",
        psf_title="Synthetic HST PSF",
        psf_cmap="gray",
        psf_floor_power=args.psf_floor_power,
        psf_upper_percentile=args.psf_upper_percentile,
        psf_dynamic_range=args.psf_dynamic_range,
        output_path=args.figure_path,
        show=not args.no_show,
    )


if __name__ == "__main__":
    main()
