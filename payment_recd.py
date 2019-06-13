import sqlite3

import logbook

from lib import utils
from lib import constants


def main():
    payment_logger = logbook.Logger('payment_recd')
    db = "well.sqlite"

    database = sqlite3.connect(f"{db}")
    cur = database.cursor()

    acct = utils.prompt_for_account("Please choose an account", cur)
    #
    # show the current balance here
    # fetch balance and display
    cur_balance = utils.get_acct_balance(acct, cur)
    if cur_balance == 0:
        print(f"This account has a zero balance.")
        exit(0)

    date = utils.prompt_for_current_date("Payment date")

    # fetch amount and flip the sign
    print(f"Current balance: ${cur_balance:.2f}")
    amt = utils.prompt_for_amount("Payment amount")
    payment_logger.debug(f"get_amount just returned this amount: {amt}")
    amt *= -1

    # cobble together the account note
    notes = "Payment on account ("
    notes += utils.prompt_for_notes("Check number")
    notes += ")"

    payment_logger.debug(date)
    payment_logger.debug(amt)
    payment_logger.debug(acct)
    payment_logger.debug(notes)

    # backup the file prior to adding any data
    utils.backup_file(db)

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
    utils.init_logging('payment_recd.log')
    main()
