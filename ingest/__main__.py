"""CLI entry point: python -m ingest"""

import argparse
import logging
import sys
from pathlib import Path

from .config import load_config
from .sources import REGISTRY


def main():
    parser = argparse.ArgumentParser(
        description="Ingest financial and economic data from free sources."
    )
    parser.add_argument(
        "--sources", nargs="+",
        help=f"Sources to run (default: all). Choices: {', '.join(REGISTRY)}",
    )
    parser.add_argument(
        "--config", default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )
    parser.add_argument(
        "--list", action="store_true", dest="list_sources",
        help="List available sources and exit.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable debug logging.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)-20s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.list_sources:
        print("Available sources:")
        for name in REGISTRY:
            print(f"  - {name}")
        return

    config = load_config(args.config)
    output_dir = Path(config["output_dir"])

    sources = args.sources or list(REGISTRY.keys())
    invalid = [s for s in sources if s not in REGISTRY]
    if invalid:
        print(f"Unknown sources: {', '.join(invalid)}", file=sys.stderr)
        print(f"Available: {', '.join(REGISTRY)}", file=sys.stderr)
        sys.exit(1)

    total_ok, total_failed = 0, 0

    for source_name in sources:
        source_config = config.get(source_name, {})
        if not source_config:
            logging.warning("No config block for '%s', skipping.", source_name)
            continue

        try:
            ingestor_cls = REGISTRY[source_name]
            ingestor = ingestor_cls(output_dir=output_dir, config=source_config)
            result = ingestor.run()
            total_ok += len(result["ok"])
            total_failed += len(result["failed"])
        except Exception:
            logging.exception("Source '%s' failed to initialize.", source_name)
            total_failed += 1

    print(f"\nDone. {total_ok} series saved, {total_failed} failed.")
    sys.exit(1 if total_failed > 0 else 0)


if __name__ == "__main__":
    main()
