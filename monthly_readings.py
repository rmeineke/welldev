import logging
import sys
import sqlite3
from lib import utils


def main():
    database = 'well.db'

    # set up for logging
    LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL,
              }
    if len(sys.argv) > 1:
        level_name = sys.argv[1]
        level = LEVELS.get(level_name, logging.NOTSET)
        logging.basicConfig(level=level)

    logger = logging.getLogger()
    logger.debug('Entering main')

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    reading_date = utils.prompt_for_current_date(logger, 'Reading date')
    cur.execute('INSERT INTO reading_dates (reading_date) VALUES (?)', (reading_date, ))
    last_inserted_row_id = cur.lastrowid

    logger.debug('attempting to backup the database file now')
    utils.backup_file(logger, database)

    cur.execute('SELECT * FROM accounts')
    rows = cur.fetchall()
    for r in rows:
        # fetch last month's reading as a sanity check
        cur.execute('SELECT reading FROM readings WHERE account_id = {} ORDER BY reading_id DESC'.format(r['acct_id']))
        last_reading = cur.fetchone()
        # print("""Last month's reading: {}""".format(last_reading['reading']))
        print(f"Last month's reading: {last_reading['reading']}")


        # grab current reading and then insert it into the DB
        reading = input("{} - {}: ".format(r['acct_id'], r['address']))
        cur.execute('INSERT INTO readings (reading_id, account_id, reading) VALUES (?,?,?)',
                    (last_inserted_row_id, r['acct_id'], reading))
        print()

    # insert into the transaction log
    cur.execute('INSERT INTO transactions_log (transaction_type, transaction_date, transaction_amount) VALUES (?, ?, ?)', (3, reading_date, 0.00))

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
