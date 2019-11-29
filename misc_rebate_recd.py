import logging
import sys
import sqlite3
from lib import utils
from lib import constants


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

    logger = logging.getLogger()
    logger.debug("Entering main")

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    rebate_date = utils.prompt_for_current_date("Rebate date")
    rebate_amount = utils.prompt_for_amount("Rebate amount")
    rebate_note = utils.prompt_for_notes("Notes")

    const = constants.Constants()
    exec_str = f"""
        INSERT INTO activity (date, type, amount, note) VALUES (?, ?, ?, ?)
    """
    params = (rebate_date, const._misc_rebate_received, rebate_amount, rebate_note)
    cur.execute(exec_str, params)
    logger.debug("attempting to backup the database file now")
    utils.backup_file(database)
        
    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == "__main__":
    main()
