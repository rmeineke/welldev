import logging
import sys
import sqlite3

#
# ./make_accounts.py logging=debug
# :


def main():
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

    db = sqlite3.connect('../well.db')
    cur = db.cursor()

    logger.debug('calling create_readings_table')
    create_readings_table(cur)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


def create_readings_table(c):
    c.execute('DROP TABLE IF EXISTS reading_dates')
    c.execute('CREATE TABLE IF NOT EXISTS \
                reading_dates(reading_date_id INTEGER PRIMARY KEY, reading_date TEXT)')

    c.execute('INSERT INTO reading_dates (reading_date) \
                    VALUES (?)', ('2018-12-27', ))


if __name__ == '__main__':
    main()



