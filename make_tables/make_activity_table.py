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
    logger.debug('make_activity_table')
    logger.debug('Entering main')

    db = sqlite3.connect('{}'.format(db))
    cur = db.cursor()

    logger.debug('calling create_activity_table')
    create_activity_table(cur, logger)
    cur.execute('INSERT INTO activity (acct, date, amount, note) \
                    VALUES (1, "2019-01-01", 0, "Opening Balance")')
    cur.execute('INSERT INTO activity (acct, date, amount, note) \
                    VALUES (2, "2019-01-01", -4680, "Opening Balance")')
    cur.execute('INSERT INTO activity (acct, date, amount, note) \
                    VALUES (3, "2019-01-01", 0, "Opening Balance")')
    cur.execute('INSERT INTO activity (acct, date, amount, note) \
                    VALUES (4, "2019-01-01", 0, "Opening Balance")')

    cur.execute('INSERT INTO activity (date, acct, type, amount, note) '
                'VALUES("2019-01-24", 2, 1, -5000, "Missing 8/2008 reading")');
    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


def create_activity_table(c, logger):
    logger.debug('inside create_activity_table')
    c.execute('DROP TABLE IF EXISTS activity')
    c.execute('CREATE TABLE IF NOT EXISTS \
                activity(id INTEGER PRIMARY KEY AUTOINCREMENT, \
                        date TEXT, \
                        acct INTEGER, \
                        type INTEGER, \
                        amount INTEGER, \
                        note TEXT)')


if __name__ == '__main__':
    main()
