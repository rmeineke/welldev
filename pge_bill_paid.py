import sqlite3
from lib import utils
from lib import constants
import logbook


def main():
    database = 'well.sqlite'
    logger = logbook.Logger('pge_bill_paid')

    utils.backup_file(database)
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # get date_paid
    payment_date = utils.prompt_for_current_date("Date paid")
    # get amount
    payment_amount = utils.prompt_for_amount("Amount paid")
    const = constants.Constants()

    # mark the bill paid in the activity account
    payment_amount = payment_amount * -1
    exec_str = f"""
                INSERT INTO activity (date, type, amount, note) 
                VALUES (?, ?, ?, ?)
            """
    params = (payment_date, const.pge_bill_paid, payment_amount, "PGE bill paid")
    logger.trace(params)
    cur.execute(exec_str, params)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    utils.init_logging('logs/pge_bill_paid.log')
    main()
