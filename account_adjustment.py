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

    logger.debug('attempting to backup the database file now')
    utils.backup_file(logger, database)

    account = utils.prompt_for_account(logger, 'Choose the affected account', cur)
    adjustment_date = utils.prompt_for_current_date(logger, 'Adjustment date')
    adjustment_amount = utils.prompt_for_amount(logger, 'Adjustment amount')
    adjustment_notes = utils.prompt_for_notes(logger, 'Adjustment notes')
    logger.debug(f'account: {account}')
    logger.debug(f'adjustment_date: {adjustment_date}')
    logger.debug(f'adjustment_amount: {adjustment_amount}')
    logger.debug(f'adjustment_notes: {adjustment_notes}')



    # insert the account
    cur.execute('INSERT INTO master_account (acct_id, date, amount, notes) VALUES (?, ?, ?, ?)', (account, adjustment_date, adjustment_amount, adjustment_notes))

    # insert into the transaction log
    cur.execute('INSERT INTO transactions_log (transaction_type, transaction_date, transaction_amount) VALUES (?, ?, ?)', (9, adjustment_date, adjustment_amount))

    # adjustment_amount = adjustment_amount * -1
    # cur.execute('INSERT INTO transactions_log (transaction_type, transaction_date, transaction_amount) VALUES (?, ?, ?)', (9, adjustment_date, adjustment_amount))

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
