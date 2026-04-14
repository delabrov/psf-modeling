#!/usr/bin/env python
"""Generate a synthetic sky scene (stars by default), no PSF convolution."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from psf_modeling.scene import generate_synthetic_scene, plot_synthetic_scene, save_scene


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nx", type=int, default=512, help="Image width in pixels.")
    parser.add_argument("--ny", type=int, default=None, help="Image height in pixels (default: nx).")
    parser.add_argument("--n-stars", type=int, default=120, help="Number of point sources.")
    parser.add_argument("--n-galaxies", type=int, default=0, help="Number of extended galaxy-like sources.")
    parser.add_argument("--n-diffuse", type=int, default=0, help="Number of diffuse components.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument(
        "--output-scene",
        type=Path,
        default=ROOT / "synthetic_scene.npy",
        help="Output path for the raw synthetic scene array.",
    )
    parser.add_argument(
        "--figure-path",
        type=Path,
        default=ROOT / "figures" / "synthetic_scene.png",
        help="Output path for the rendered synthetic scene figure.",
    )
    parser.add_argument("--no-show", action="store_true", help="Do not open a display window.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    scene = generate_synthetic_scene(
        nx=args.nx,
        ny=args.ny,
        n_stars=args.n_stars,
        n_galaxies=args.n_galaxies,
        n_diffuse=args.n_diffuse,
        seed=args.seed,
    )

    save_scene(args.output_scene, scene)
    plot_synthetic_scene(
        scene,
        output_path=args.figure_path,
        show=not args.no_show,
    )

    print(f"Scene array saved to {args.output_scene}")
    print(f"Scene figure saved to {args.figure_path}")


if __name__ == "__main__":
    main()
