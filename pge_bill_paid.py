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
    utils.backup_file(logger, database)
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # get date_paid
    payment_date = utils.prompt_for_current_date(logger, "Date paid")
    # get amount
    payment_amount = utils.prompt_for_amount(logger, "Amount paid")

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
    # 2019.02.19 ... had to tweak this as it was grabbing the wrong amount due to a sorting error
    cur.execute(f'SELECT amount FROM master_account WHERE acct_id = {master_acct_id} and notes like "%PGE Bill Share%" ORDER BY date DESC LIMIT 1')
    last_billing_amt = cur.fetchone()[0]
    logger.debug(f'last_billing_amt: {last_billing_amt}')

    # credit the master account with the equivalent payment
    last_billing_amt = last_billing_amt * -1
    cur.execute('INSERT INTO master_account (acct_id, date, amount, notes) VALUES (?,?,?,?)',
                (master_acct_id, payment_date, last_billing_amt , "PGE Bill Paid"))

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()

#
# sqlite> select amount  from master_account where acct_id = 3;
# 0
# 3149
# 1335
# 0
# sqlite> select amount  from master_account where acct_id = 3 and notes like '%PGE Bill Share%';
# 3149
# sqlite>
