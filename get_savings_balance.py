import logging
import sqlite3
import sys
import datetime
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
    logger.debug(datetime.date.today().isoformat())

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    cur_balance = utils.get_savings_balance(logger, cur)
    print()
    print('------------------------------------------------------')
    print(f'Current savings balance: ${(cur_balance / 100):,.2f}')
    print('------------------------------------------------------')
    print()

    # close the cursor and db
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
