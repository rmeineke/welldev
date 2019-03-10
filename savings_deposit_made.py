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

    # present the last savings assessment here ...
    cur.execute('SELECT transaction_amount FROM transactions_log WHERE transaction_type = 6 ORDER BY transaction_date DESC LIMIT 1')
    last_assessment = cur.fetchone()[0]
    print(f'last_assessment amount: {last_assessment / 100:.2f}')

    # get date_paid
    deposit_date = utils.prompt_for_current_date(logger, "Date deposit made")
    # get amount
    deposit_amount = utils.prompt_for_amount(logger, "Amount of deposit")

    # insert into the transaction log
    deposit_amount = deposit_amount * -1
    cur.execute('INSERT INTO transactions_log (transaction_type, transaction_date, transaction_amount) VALUES (?, ?, ?)',
                (7, deposit_date, deposit_amount))

    # mark the main account as paid
    cur.execute('SELECT acct_id FROM accounts WHERE master = "yes"')

    # fetchone ROW .... zeroeth item is the account number
    master_acct_id = cur.fetchone()[0]
    logger.debug(f'master_acct_id: {master_acct_id}')

    # go to the master account
    # find the last billing amount
    cur.execute(f'SELECT amount FROM master_account WHERE acct_id = {master_acct_id} and notes like "%Savings Assessment%" ORDER BY date DESC LIMIT 1')
    last_savings_assessment = cur.fetchone()[0]
    logger.debug(f'last_billing_amt: {last_savings_assessment}')

    # credit the master account with the equivalent payment
    last_savings_assessment = last_savings_assessment * -1
    cur.execute('INSERT INTO master_account (acct_id, date, amount, notes) VALUES (?,?,?,?)',
                (master_acct_id, deposit_date, last_savings_assessment, "Payment on account (Savings Deposit.)"))

    # insert into the transaction log
    cur.execute(
        "INSERT INTO transactions_log (acct_id, transaction_type, transaction_date, transaction_amount) "
        "VALUES (?, ?, ?, ?)",
        (master_acct_id, 3, deposit_date, last_savings_assessment),
    )

    # prompt for notes ... 'Dep for Jan 2019' ... or similar
    notes = utils.prompt_for_notes(logger, 'Notes for this deposit')
    deposit_amount = deposit_amount * -1
    # sigh, of course we then need to add the deposit to the savings account table
    cur.execute('INSERT INTO savings_account (date, amount, notes) VALUES (?,?,?)',
                (deposit_date, deposit_amount, notes))

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()

