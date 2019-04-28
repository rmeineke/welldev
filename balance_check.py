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

    print(f"")
    utils.print_account_balances(logger, cur)
    print(f"")
    utils.print_savings_account_balance(logger, cur)
    print(f"")
    # utils.print_main_account_balance(logger, cur)
    # print(f"")

    # close the cursor and db
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
