import logbook
import sqlite3
from lib import constants
from lib import utils


def main():
    savings_logger = logbook.Logger("get_savings_bal.log")
    database = "well.sqlite"

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    exec_str = f"""
        SELECT SUM(amount) 
        FROM activity
        WHERE type = (?)
        OR type = (?)
        OR type = (?)
    """
    const = constants.Constants()
    params = (
        const.savings_deposit_made,
        const.savings_disbursement,
        const.savings_dividend,
    )
    cur.execute(exec_str, params)
    current_savings_balance = cur.fetchone()[0]
    savings_logger.trace(f"current_savings_balance: {current_savings_balance}")
    print(f"===============================================")
    print(f" current savings balance: $ {current_savings_balance/100:,.2f}")
    print(f"===============================================")

    # close the cursor and db
    cur.close()
    db.close()


if __name__ == "__main__":
    utils.init_logging("get_savings_bal.log")
    main()
