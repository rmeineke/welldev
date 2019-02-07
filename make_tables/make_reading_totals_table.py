import logging
import sys
import sqlite3


def main():
    db = '../well.db'

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
    logger.debug('Entering Main')

    db = sqlite3.connect('{}'.format(db))
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    create_readings_total_table(cur, logger)
    #
    # cur.execute("SELECT reading_date_id FROM ")



    for idx in range(1,223):
        ttl = 0.0
        for acct in range(1, 5):

            cur.execute(f"SELECT account_id, reading FROM readings WHERE reading_id = {idx} AND account_id = {acct}")
            row1 = cur.fetchone()
            print(f'{idx}..{row1["account_id"]} -- {row1["reading"]}')
            cur.execute(f"SELECT account_id, reading FROM readings WHERE reading_id = {idx + 1} AND account_id = {acct}")
            row2 = cur.fetchone()
            print(f'{idx + 1}..{row2["account_id"]} -- {row2["reading"]}')

            if row1['account_id'] is 1:
                diff = row2["reading"] - row1["reading"]
            else:
                diff = (row2["reading"] - row1["reading"]) * 7.48052
            ttl += diff
            print(f'------------------------')
        print(f'{ttl}')

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


def create_readings_total_table(c, logger):
    logger.debug('inside create_readings_table')
    c.execute('DROP TABLE IF EXISTS readings_totals')
    c.execute('CREATE TABLE IF NOT EXISTS \
                readings_totals(reading_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                        total REAL)')


if __name__ == '__main__':
    main()
