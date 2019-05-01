import logging
import sys
import sqlite3
from lib import utils
from lib import constants
import account


def main():
    database = "well.db"

    # set up for logging
    LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    if len(sys.argv) > 1:
        level_name = sys.argv[1]
        level = LEVELS.get(level_name, logging.NOTSET)
        logging.basicConfig(level=level)

    logger = logging.getLogger()
    logger.debug("Entering main")

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    last_pge_bill_recd_date = utils.get_last_pge_bill_recd_date(cur, logger)
    logger.debug(f"last_pge_bill_recd_date: {last_pge_bill_recd_date}")

    acct_list = []
    cur.execute("SELECT * FROM account")
    rows = cur.fetchall()
    ttl_monthly_usage = 0
    for r in rows:
        # init the accounts
        logger.debug(f"\ninit an account ... add to acct list ... {r['last_name']} ... {r['acct_id']}")
        acct_obj = account.Account(r['acct_id'], r['first_name'], r['last_name'], r['address'], r['reads_in'], ['master'])
        acct_list.append(acct_obj)

        # get and set the previous balance
        prev_balance = utils.get_prev_balance(cur, acct_obj.acct_id, last_pge_bill_recd_date, logger)
        if prev_balance is None:
            prev_balance = 0
        acct_obj.prev_balance = prev_balance
        logger.debug(f"prev_balance: {prev_balance}")

        # new charges
        new_charges = utils.get_new_charges(cur, acct_obj.acct_id, last_pge_bill_recd_date, logger)
        if new_charges is None:
            new_charges = 0
        logger.debug(f"new_charges: {new_charges}")

        # adjustments?
        adjustments = utils.get_adjustments(cur, acct_obj.acct_id, last_pge_bill_recd_date, logger)
        if adjustments is None:
            adjustments = 0
        logger.debug(f"adjustments: {adjustments}")

        # check for any payments made
        payments = utils.get_payments(cur, acct_obj.acct_id, last_pge_bill_recd_date, logger)
        if payments is None:
            payments = 0
        logger.debug(f"payments: {payments}")

        # show account balance
        balance = prev_balance + new_charges + adjustments + payments
        logger.debug(f"balance: {balance}")

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == "__main__":
    main()
