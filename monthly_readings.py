import sqlite3
from lib import utils
import logbook


def main():
    reading_logger = logbook.Logger("readings")
    database = "well.sqlite"

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    reading_date: str = utils.prompt_for_current_date("Reading date")
    exec_str = "INSERT INTO reading_date (date) VALUES (?)"
    params = (reading_date,)
    reading_logger.trace(f"{exec_str}{params}")
    cur.execute(exec_str, params)
    last_inserted_row_id = cur.lastrowid

    reading_logger.trace("attempting to backup the database file now")
    backup_file_name = utils.backup_file(database)
    reading_logger.trace(f"database backed up to: {backup_file_name}")

    exec_str = "SELECT * FROM account"
    cur.execute(exec_str)
    rows = cur.fetchall()
    for r in rows:
        if r["active"] == "no":
            reading_logger.trace(f"Account {r['acct_id']} currently INACTIVE")
            continue

        # fetch last month's reading as a sanity check
        exec_str = f"""
            SELECT reading
            FROM reading
            WHERE account_id = (?)
            ORDER BY reading_id
            DESC
        """
        params = (r["acct_id"],)
        cur.execute(exec_str, params)
        last_reading = cur.fetchone()
        print(f"Last month's reading: {last_reading['reading']}")

        # grab current reading and then insert it into the DB
        reading = input(f"{r['acct_id']} - {r['address']}: ")

        # this should allow empty input .... in case of inactive account
        if not reading:
            continue

        exec_str = f"""
            INSERT INTO reading (reading_id, account_id, reading)
            VALUES (?, ?, ?)
        """
        params = (last_inserted_row_id, r["acct_id"], reading)
        reading_logger.trace(params)
        cur.execute(exec_str, params)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == "__main__":
    utils.init_logging("logs/monthly_readings.log")
    main()
