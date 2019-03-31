import logging
import sqlite3
import sys
import constants


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

    exec_str = f"""
        SELECT SUM(amount) 
        FROM activity
        WHERE type = (?)
        OR type = (?)
        OR type = (?)
    """
    const = constants.Constants()
    params = (const.savings_deposit, const.savings_disbursement, const.savings_deposit)
    cur.execute(exec_str, params)
    current_savings_balance = cur.fetchone()[0]
    logger.debug(f"current_savings_balance: {current_savings_balance}")
    print(f"===============================================")
    print(f" current savings balance: $ {current_savings_balance/100:,.2f}")
    print(f"===============================================")

    # close the cursor and db
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
