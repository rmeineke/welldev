import logging
import sys
import sqlite3
from logging import Logger
from lib import utils


def main():
    database = "well.sqlite"

    # set up for logging
    LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    if len(sys.argv) > 1:
        level_name = sys.argv[1]
        level = LEVELS.get(level_name, logging.NOTSET)
        logging.basicConfig(level=level)

    logger: Logger = logging.getLogger()
    logger.debug("Entering main")

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    logger.debug("attempting to backup the database file now")
    backup_file_name: str = utils.backup_file(logger, database)
    logger.debug(f'database backed up to: {backup_file_name}')

    reading_date = utils.prompt_for_current_date(logger, "Reading date")
    exec_str: str = "INSERT INTO reading_date (date) VALUES (?)"
    params = (reading_date, )
    logger.debug(f"{exec_str}{params}")
    cur.execute(exec_str, params)
    last_inserted_row_id = cur.lastrowid
    logger.debug(f"last_inserted_row_id: {last_inserted_row_id}")
    acct: str = utils.prompt_for_account(logger, "Please choose an account", cur)
    reading: str = input(f"Reading: ")
    exec_str = "INSERT INTO reading (reading_id, account_id, reading) VALUES (?, ?, ?)"
    params = (last_inserted_row_id, int(acct), int(reading))
    cur.execute(exec_str, params)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == "__main__":
    main()
