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

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    logger.debug('attempting to backup the database file now')
    utils.backup_file(logger, database)

    const = constants.Constants()
    account = utils.prompt_for_account(logger, 'Choose the affected account', cur)
    adjustment_date = utils.prompt_for_current_date(logger, 'Adjustment date')
    adjustment_amount = utils.prompt_for_amount(logger, 'Adjustment amount')
    # adjustment_amount *= -1
    adjustment_note = utils.prompt_for_notes(logger, 'Adjustment note')
    logger.debug(f'account: {account}')
    adjustment_date = f"{adjustment_date}"
    logger.debug(f'adjustment_date: {adjustment_date}')
    logger.debug(f'adjustment_amount: {adjustment_amount}')
    logger.debug(f'adjustment_note: {adjustment_note}')
    adjustment_note = f"{adjustment_note}"

    # insert the account
    query = f"""
        INSERT INTO activity (acct, date, type, amount, note) 
        VALUES (?, ?, ?, ?, ?)
    """
    params = (account, adjustment_date, const.account_adjustment, adjustment_amount, adjustment_note)
    cur.execute(query, params)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
