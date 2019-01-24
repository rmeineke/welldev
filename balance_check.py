import logging
import sys
import sqlite3
import datetime


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
    logger.debug(datetime.date.today().isoformat())

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    balances = {}
    balances = get_account_balances(cur, logger)
    print(balances)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


def get_account_balances(cur, logger):
    logger.debug('Entering get_account_balances')
    accts = {}

    # loop through and get acct ids
    # then get each balance and return
    cur.execute('SELECT acct_id, last_name FROM accounts')
    rows = cur.fetchall()
    for r in rows:
        bal_row = cur.execute('SELECT SUM(amount) FROM master_account WHERE acct_id = {}'.format(r['acct_id']))
        bal = bal_row.fetchone()[0]
        print('{} -- {:10} ..... {:>8,.2f}'.format(r['acct_id'], r['last_name'], bal / 100))

    accts['Schultz'] = 100
    return accts


if __name__ == '__main__':
    main()
