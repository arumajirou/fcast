from __future__ import annotations
import argparse
from fcast.logging import setup_logging
from fcast.config import settings
from fcast.meta.db import init_db

def app():
    parser = argparse.ArgumentParser(prog="fcast")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("init-db", help="Create meta DB tables (forecast_meta).")

    args = parser.parse_args()
    setup_logging(settings.log_level)

    if args.cmd == "init-db":
        init_db()
        print("OK: meta DB initialized")
    else:
        parser.print_help()

if __name__ == "__main__":
    app()
