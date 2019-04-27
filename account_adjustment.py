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

    const = constants.Constants()
    print(f'{const.account_adjustment}')

    logger.debug('attempting to backup the database file now')
    utils.backup_file(logger, database)

    account = utils.prompt_for_account(logger, 'Choose the affected account', cur)
    adjustment_date = utils.prompt_for_current_date(logger, 'Adjustment date')
    adjustment_amount = utils.prompt_for_amount(logger, 'Adjustment amount')
    adjustment_amount *= -1
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
#
#
# 1
#
# The problem here is understanding parameterization - it works only for parameters, not for column names and other stuff.
#
# in this example:
#
#  query = 'SELECT * FROM foo WHERE bar = ? AND baz = ?'
#  params = (a, b)
#  cursor.execute(query, params)
#
# Note that the query and the data are passed separately to .execute - it is the database's job to do the interpolation - that frees you from quote hell, and makes your program safer by disabling any kind of sql injection. It also could perform better - it allows the database to cache the compiled query and use it when you change parameters.
#
# Now that only works for data. If you want to have the actual column name in a variable, you have to interpolate it yourself in the query:
#
#  col1 = 'bar'
#  col2 = 'baz'
#  query = f'SELECT * FROM foo WHERE {col1} = ? AND {col2} = ?'
#  cursor.execute(query, params)
#
# shareeditflag
