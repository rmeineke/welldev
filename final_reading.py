import logging
import sys
import sqlite3
from lib import utils


def main():
    database = "well.db"

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

    logger.debug("attempting to backup the database file now")
    utils.backup_file(logger, database)

    reading_date = utils.prompt_for_current_date(logger, "Reading date")
    exec_str = f"""
        INSERT INTO reading_date (date) 
        VALUES (?)
    """
    params = (reading_date, )
    logger.debug(f"{exec_str}{params}")
    cur.execute(exec_str, params)
    last_inserted_row_id = cur.lastrowid
    logger.debug(f"last_inserted_row_id: {last_inserted_row_id}")
    acct = utils.prompt_for_account(logger, "Please choose an account", cur)
    reading = input(f"Reading: ")
    exec_str = f"""
            INSERT INTO reading (reading_id, account_id, reading)
            VALUES (?, ?, ?)
        """
    params = (last_inserted_row_id, acct, reading)
    cur.execute(exec_str, params)

    # exec_str = f"""
    #     SELECT * FROM account
    # """
    # cur.execute(exec_str)
    # rows = cur.fetchall()
    # for r in rows:
    #     # fetch last month's reading as a sanity check
    #     exec_str = f"""
    #         SELECT reading
    #         FROM reading
    #         WHERE account_id = (?)
    #         ORDER BY reading_id
    #         DESC
    #     """
    #     params = (r["acct_id"], )
    #     cur.execute(exec_str, params)
    #     last_reading = cur.fetchone()
    #     print(f"Last month's reading: {last_reading['reading']}")
    #
    #     # grab current reading and then insert it into the DB
    #     reading = input(f"{r['acct_id']} - {r['address']}: ")
    #     exec_str = f"""
    #         INSERT INTO reading (reading_id, account_id, reading)
    #         VALUES (?, ?, ?)
    #     """
    #     params = (last_inserted_row_id, r["acct_id"], reading)
    #     cur.execute(exec_str, params)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == "__main__":
    main()