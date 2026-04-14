#!/usr/bin/env python
"""Load a saved JWST pupil and display its PSF."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from psf_modeling import build_jwst_pupil, compute_psf, load_pupil, plot_pupil_and_psf, save_pupil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pupil-path",
        type=Path,
        default=ROOT / "pupil_JWST.dat",
        help="Path to a saved pupil (.npy or text).",
    )
    parser.add_argument(
        "--fallback-dat",
        type=Path,
        default=ROOT / "pupil_JWST.dat",
        help="Fallback text path if --pupil-path is missing.",
    )
    parser.add_argument(
        "--figure-path",
        type=Path,
        default=ROOT / "figures" / "jwst_pupil_psf.png",
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


def resolve_pupil(path: Path, fallback_dat: Path) -> np.ndarray:
    if path.exists():
        try:
            return load_pupil(path)
        except (OSError, ValueError):
            pass
    if fallback_dat != path and fallback_dat.exists():
        try:
            return load_pupil(fallback_dat)
        except (OSError, ValueError):
            pass

    pupil = build_jwst_pupil()
    save_pupil(path, pupil)
    if fallback_dat != path:
        save_pupil(fallback_dat, pupil)
    return pupil


def main() -> None:
    args = parse_args()

    pupil_jwst = resolve_pupil(args.pupil_path, args.fallback_dat)
    psf_jwst = compute_psf(pupil_jwst)

    nx = pupil_jwst.shape[0]
    x = np.arange(nx) - nx // 2

    plot_pupil_and_psf(
        pupil=pupil_jwst,
        psf=psf_jwst,
        coords=x,
        pupil_title="Synthetic JWST Pupil",
        psf_title="Synthetic JWST PSF",
        psf_cmap="gray",
        psf_floor_power=args.psf_floor_power,
        psf_upper_percentile=args.psf_upper_percentile,
        psf_dynamic_range=args.psf_dynamic_range,
        output_path=args.figure_path,
        show=not args.no_show,
    )


if __name__ == "__main__":
    main()
