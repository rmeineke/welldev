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
    logger.debug('make_master_account_table')
    logger.debug('Entering main')

    db = sqlite3.connect('{}'.format(db))
    cur = db.cursor()

    logger.debug('calling create_master_account_table')
    create_master_account_table(cur, logger)
    cur.execute('INSERT INTO master_account (acct_id, date, amount, notes) \
                    VALUES (1, "2019-01-01", 0, "Opening Balance")')
    cur.execute('INSERT INTO master_account (acct_id, date, amount, notes) \
                    VALUES (2, "2019-01-01", -4680, "Opening Balance")')
    cur.execute('INSERT INTO master_account (acct_id, date, amount, notes) \
                    VALUES (3, "2019-01-01", 0, "Opening Balance")')
    cur.execute('INSERT INTO master_account (acct_id, date, amount, notes) \
                    VALUES (4, "2019-01-01", 0, "Opening Balance")')

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


def create_master_account_table(c, logger):
    logger.debug('inside create_master_account_table')
    c.execute('DROP TABLE IF EXISTS master_account')
    c.execute('CREATE TABLE IF NOT EXISTS \
                master_account(transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                        acct_id INTEGER, \
                        date TEXT, \
                        amount INTEGER, \
                        notes TEXT)')

if __name__ == '__main__':
    main()
