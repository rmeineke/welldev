import logging
import sqlite3
import sys
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

    cur_balance = get_master_account_balance(cur, logger)
    print()
    print('-------------------------------------------------------------------------')
    print(f'Current master account balance: ${(cur_balance / 100):,.2f}')
    print('-------------------------------------------------------------------------')

    print()

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


def get_master_account_balance(cur, logger):
    logger.debug('Entering get_savings_balance()')
    row = cur.execute("SELECT sum(amount) from master_account")
    cur_balance = row.fetchone()[0]
    return cur_balance


if __name__ == '__main__':
    main()