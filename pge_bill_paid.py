import logging
import sys
import sqlite3
import account
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
    utils.backup_file(logger, database)
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # get date_paid
    payment_date = utils.prompt_for_current_date(logger, "Date paid")
    # get amount
    payment_amount = utils.get_amount(logger, "Amount paid")


    # insert into the transaction log
    payment_amount = payment_amount * -1
    cur.execute('INSERT INTO transactions_log (transaction_type, transaction_date, transaction_amount) VALUES (?, ?, ?)',
                (4, payment_date, payment_amount))

    # mark the main account as paid
    cur.execute('SELECT acct_id FROM accounts WHERE master = "yes"')

    # fetchone ROW .... zeroeth item is the account number
    master_acct_id = cur.fetchone()[0]
    logger.debug(f'master_acct_id: {master_acct_id}')

    # go to the master account
    # find the last billing amount
    cur.execute(f'SELECT amount FROM master_account WHERE acct_id = {master_acct_id}')
    last_billing_amt = cur.fetchone()[0]
    logger.debug(f'last_billing_amt: {last_billing_amt}')

    # credit the master account with the equivalent payment
    last_billing_amt = last_billing_amt * -1
    cur.execute('INSERT INTO master_account (account_id, date, amount, notes) VALUES (?,?,?,?)',
                (master_acct_id, date_paid, last_billing_amt , "PGE Bill Paid"))

    # cur.execute('INSERT INTO master_account (account_id, date, amount) VALUES (?,?,?)',
    #             (master_acct_id, r['acct_id'], reading))

    # update transactions log


    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
