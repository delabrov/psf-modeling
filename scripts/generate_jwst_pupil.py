#!/usr/bin/env python
"""Generate and save the simplified JWST pupil arrays."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from psf_modeling import build_jwst_pupil, save_pupil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nx", type=int, default=512)
    parser.add_argument("--segment-radius", type=float, default=54.0)
    parser.add_argument("--segment-gap", type=float, default=2.0)
    parser.add_argument("--spider-width", type=int, default=6)
    parser.add_argument(
        "--output-dat",
        type=Path,
        default=ROOT / "pupil_JWST.dat",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pupil = build_jwst_pupil(
        nx=args.nx,
        segment_radius=args.segment_radius,
        segment_gap=args.segment_gap,
        spider_width=args.spider_width,
    )
    save_pupil(args.output_dat, pupil)
    print(f"Saved pupil to {args.output_dat}")


if __name__ == "__main__":
    main()
