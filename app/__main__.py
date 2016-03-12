import os
import sys
import threading

from .app import log, app


if __name__ == '__main__':
    import argparse

    if "GITHUB_API_TOKEN" not in os.environ:
        log.info("GITHUB_API_TOKEN not set")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    log.info("Starting front-end..")
    app.debug = args.debug
    app.run(host=os.getenv("IP", '0.0.0.0'),
            port=int(os.getenv("PORT", 8080)))
