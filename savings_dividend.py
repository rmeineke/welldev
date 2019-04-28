import logging
import sys
import sqlite3
from lib import utils
from lib import constants


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
    utils.backup_file(logger, database)
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # check current balance here
    const = constants.Constants()
    exec_str = f"""
        SELECT SUM(amount)
        FROM activity 
        WHERE type = (?)
        OR type = (?)
        OR type = (?)
    """
    params = (const.savings_deposit_made, const.savings_disbursement, const.savings_dividend)
    logger.debug(f"params: {params}")
    cur.execute(exec_str, params)
    current_savings_balance = cur.fetchone()[0]
    logger.debug(f"current_savings_balance: {current_savings_balance}")
    print(f"===============================================")
    print(f" current savings balance: ${current_savings_balance / 100:,.2f}")
    print(f"===============================================")

    # get date_paid
    dividend_date = utils.prompt_for_current_date(logger, "Date of dividend")
    # get amount
    dividend_amount = utils.prompt_for_amount(logger, "Amount of dividend")
    # prompt for notes ... 'Dep for Jan 2019' ... or similar
    note = f"Savings dividend"

    # enter into the activity log
    exec_str = f"""
        INSERT INTO activity (date, type, amount, note) 
        VALUES (?, ?, ?, ?)
    """
    params = (dividend_date, const.savings_dividend, dividend_amount, note)
    cur.execute(exec_str, params)

    # check the balance again
    exec_str = f"""
            SELECT SUM(amount)
            FROM activity 
            WHERE type = (?)
            OR type = (?)
            OR type = (?)
        """
    params = (const.savings_deposit_made, const.savings_disbursement, const.savings_dividend)
    print(f"{params}")
    cur.execute(exec_str, params)
    current_savings_balance = cur.fetchone()[0]
    logger.debug(f"current_savings_balance: {current_savings_balance}")
    print(f"===============================================")
    print(f" current savings balance: ${current_savings_balance / 100: ,.2f}")
    print(f"===============================================")

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
