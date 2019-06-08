import sys

import click
import logbook as logbook


@click.command()
@click.option('--address', '-a')
def main(address):
    pass


def init_logging(filename: str = None):
    level = logbook.TRACE
    if filename:
        logbook.TimedRotatingFileHandler(filename, level=level).push_application()
    else:
        logbook.StreamHandler(sys.stdout, level=level).push_application()
    msg = f"Logging initialized: level = {level}"

    logger = logbook.Logger('Startup')
    logger.notice(msg)


if __name__ == "__main__":
    init_logging()
    main()
