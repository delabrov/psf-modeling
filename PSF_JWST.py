#!/usr/bin/env python
"""Generate a simplified JWST pupil, compute its PSF, and plot both."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from psf_modeling import build_jwst_pupil, compute_psf, plot_pupil_and_psf, save_pupil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nx", type=int, default=512, help="Image size in pixels.")
    parser.add_argument("--segment-radius", type=float, default=54.0, help="Hex segment radius in pixels.")
    parser.add_argument("--segment-gap", type=float, default=2.0, help="Gap between segments in pixels.")
    parser.add_argument("--spider-width", type=int, default=6, help="Spider width in pixels.")
    parser.add_argument(
        "--output-pupil-dat",
        type=Path,
        default=ROOT / "pupil_JWST.dat",
        help="Path to save the pupil text map.",
    )
    parser.add_argument(
        "--figure-path",
        type=Path,
        default=ROOT / "figures" / "jwst_pupil_psf.png",
        help="Output path for the generated figure.",
    )
    parser.add_argument("--no-show", action="store_true", help="Do not open a display window.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pupil_jwst = build_jwst_pupil(
        nx=args.nx,
        segment_radius=args.segment_radius,
        segment_gap=args.segment_gap,
        spider_width=args.spider_width,
    )
    psf_jwst = compute_psf(pupil_jwst)

    save_pupil(args.output_pupil_dat, pupil_jwst)

    x = np.arange(args.nx) - args.nx // 2
    plot_pupil_and_psf(
        pupil=pupil_jwst,
        psf=psf_jwst,
        coords=x,
        pupil_title="JWST Pupil",
        psf_title="JWST PSF",
        psf_cmap="gray",
        output_path=args.figure_path,
        show=not args.no_show,
    )


if __name__ == "__main__":
    main()
