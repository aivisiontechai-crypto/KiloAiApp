import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.cli.main import main as cli_main

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Live Trading Platform")
    parser.add_argument("command", choices=["web", "start", "status", "portfolio", "performance"])
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    if args.command == "web":
        from web.server import start_server
        asyncio.run(start_server(args.host, args.port))
    elif args.command == "start":
        cli_main()
    else:
        cli_main()


if __name__ == "__main__":
    main()
