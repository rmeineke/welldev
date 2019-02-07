import logging
import sys
import sqlite3
from lib import utils


def get_acct_balance(acct, cur):
    row = cur.execute(
        f"SELECT sum(amount) from master_account WHERE acct_id = {acct}"
    )
    bal = row.fetchone()[0]
    return bal / 100


def main():
    db = "well.db"

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
    logger.debug("payment_recd")
    logger.debug("entering main")

    db = sqlite3.connect(f"{db}")
    cur = db.cursor()

    acct = utils.prompt_for_account(logger, "Please choose an account", cur)
    date = utils.prompt_for_current_date(logger, "Payment date")

    # fetch amount and flip the sign
    amt = utils.prompt_for_amount(logger, "Payment amount")
    logger.debug(f"get_amount just returned this amount: {amt}")
    amt *= -1

    # cobble together the account note
    notes = "Payment on account. "
    notes += utils.prompt_for_notes(logger, "Check number")
    notes += "."

    logger.debug(date)
    logger.debug(amt)
    logger.debug(acct)
    logger.debug(notes)

    # fetch balance and display
    cur_balance = get_acct_balance(acct, cur)
    print(f"\n\nCurrent balance:\t{cur_balance:.2f}")

    # backup the file prior to adding any data
    utils.backup_file(logger, db)

    # insert the account
    cur.execute(
        "INSERT INTO master_account (acct_id, date, amount, notes) VALUES (?, ?, ?, ?)",
        (acct, date, amt, notes),
    )

    # insert into the transaction log
    cur.execute(
        "INSERT INTO transactions_log (acct_id, transaction_type, transaction_date, transaction_amount) "
        "VALUES (?, ?, ?, ?)",
        (acct, 3, date, amt),
    )

    # fetch updated balance and display
    cur_balance = get_acct_balance(acct, cur)
    print(f"Updated balance:\t{cur_balance:.2f}\n")

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == "__main__":
    main()
