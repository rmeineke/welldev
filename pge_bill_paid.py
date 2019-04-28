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

    # get date_paid
    payment_date = utils.prompt_for_current_date(logger, "Date paid")
    # get amount
    payment_amount = utils.prompt_for_amount(logger, "Amount paid")

    # # mark the main account as paid
    # cur.execute('SELECT acct_id FROM account WHERE master = "yes"')
    #
    # # fetchone ROW .... zeroeth item is the account number
    # master_acct_id = cur.fetchone()[0]
    # logger.debug(f'master_acct_id: {master_acct_id}')
    #
    # # go to the master account
    # # find the last billing amount
    # # 2019.02.19 ... had to tweak this as it was grabbing the wrong amount due to a sorting error
    # exec_str = f"""
    #     SELECT amount
    #     FROM activity
    #     WHERE acct = (?)
    #     AND note
    #     LIKE "%PGE bill share%"
    #     ORDER BY date
    #     DESC LIMIT 1
    # """
    # params = (master_acct_id, )
    # cur.execute(exec_str, params)
    # last_billing_amt = cur.fetchone()[0]
    # logger.debug(f'last_billing_amt: {last_billing_amt}')

    const = constants.Constants()

    # mark the bill paid in the activity account
    payment_amount = payment_amount * -1
    exec_str = f"""
                INSERT INTO activity (date, type, amount, note) 
                VALUES (?, ?, ?, ?)
            """
    params = (payment_date, const.pge_bill_paid, payment_amount, "PGE bill paid")
    cur.execute(exec_str, params)

    # # credit the master account with the equivalent payment
    # last_billing_amt = last_billing_amt * -1
    # exec_str = f"""
    #     INSERT INTO activity (date, acct, type, amount, note)
    #     VALUES (?, ?, ?, ?, ?)
    # """
    # params = (payment_date, master_acct_id, const.payment, last_billing_amt, "Payment on account (PGE bill paid)")
    # cur.execute(exec_str, params)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
