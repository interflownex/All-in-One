from __future__ import annotations

import argparse
import logging
import time

from modules.shared.outbox_dispatcher import OutboxDispatcher, OutboxSettings


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish transactional outbox events to RabbitMQ.")
    parser.add_argument("--loop", action="store_true", help="Keep polling after each batch.")
    args = parser.parse_args()
    settings = OutboxSettings.from_environment()
    dispatcher = OutboxDispatcher(settings)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        while True:
            summary = dispatcher.publish_batch()
            logging.info(
                "outbox batch selected=%d published=%d failed=%d",
                summary.selected,
                summary.published,
                summary.failed,
            )
            if not args.loop:
                return 1 if summary.failed else 0
            time.sleep(settings.poll_seconds)
    except KeyboardInterrupt:
        return 0
    finally:
        dispatcher.close()


if __name__ == "__main__":
    raise SystemExit(main())
