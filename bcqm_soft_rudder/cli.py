from __future__ import annotations

import argparse
from pathlib import Path

from .simulate import run_scan


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="BCQM IV_c soft-rudder single-thread W_coh scan",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_p = subparsers.add_parser("run", help="run a W_coh scan from a YAML config")
    run_p.add_argument("config", type=str, help="Path to YAML config file")

    args = parser.parse_args(argv)

    if args.command == "run":
        config_path = Path(args.config)
        run_scan(config_path)
    else:
        parser.error(f"Unknown command {args.command!r}")


if __name__ == "__main__":
    main()
