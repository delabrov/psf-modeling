#!/usr/bin/env python
"""Render JWST pupil and PSF figure from a saved pupil file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
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
    )
    parser.add_argument(
        "--figure-path",
        type=Path,
        default=ROOT / "figures" / "jwst_pupil_psf.png",
    )
    parser.add_argument("--no-show", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.pupil_path.exists():
        pupil = load_pupil(args.pupil_path)
    else:
        pupil = build_jwst_pupil()
        save_pupil(args.pupil_path, pupil)

    psf = compute_psf(pupil)
    nx = pupil.shape[0]
    x = np.arange(nx) - nx // 2

    plot_pupil_and_psf(
        pupil=pupil,
        psf=psf,
        coords=x,
        pupil_title="JWST Pupil",
        psf_title="JWST PSF",
        psf_cmap="gray",
        output_path=args.figure_path,
        show=not args.no_show,
    )

    print(f"Figure written to {args.figure_path}")


if __name__ == "__main__":
    main()
