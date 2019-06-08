import logging
import sys
import sqlite3
from lib import utils
from lib import constants


def main():
    db = "well.sqlite"

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

    database = sqlite3.connect(f"{db}")
    cur = database.cursor()

    acct = utils.prompt_for_account(logger, "Please choose an account", cur)
    #
    # show the current balance here
    # fetch balance and display
    cur_balance = utils.get_acct_balance(acct, cur)
    if cur_balance == 0:
        print(f"This account has a zero balance.")
        exit(0)

    date = utils.prompt_for_current_date(logger, "Payment date")

    # fetch amount and flip the sign
    print(f"Current balance: ${cur_balance:.2f}")
    amt = utils.prompt_for_amount(logger, "Payment amount")
    logger.debug(f"get_amount just returned this amount: {amt}")
    amt *= -1

    # cobble together the account note
    notes = "Payment on account ("
    notes += utils.prompt_for_notes(logger, "Check number")
    notes += ")"

    logger.debug(date)
    logger.debug(amt)
    logger.debug(acct)
    logger.debug(notes)

    # backup the file prior to adding any data
    utils.backup_file(logger, db)

    const = constants.Constants()
    # insert the account
    cur.execute(
        "INSERT INTO activity (date, acct, type, amount, note) VALUES (?, ?, ?, ?, ?)",
        (date, acct, const.payment_received, amt, notes),
    )

    # fetch updated balance and display
    cur_balance = utils.get_acct_balance(acct, cur)
    print(f"Updated balance: ${cur_balance:.2f}\n")

    # save, then close the cursor and database
    database.commit()
    cur.close()
    database.close()


if __name__ == "__main__":
    main()
