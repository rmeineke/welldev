import sqlite3
from lib import utils
from lib import constants
import logbook

def main():
    database = 'well.sqlite'
    logger = logbook.Logger("savings_dividend")
    logger.debug('Entering main')
    utils.backup_file(database)
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # check current balance here
    const = constants.Constants()
    exec_str = f"""
        SELECT SUM(amount)
        FROM activity 
        WHERE type = (?)
        OR type = (?)
        OR type = (?)
    """
    params = (const.savings_deposit_made, const.savings_disbursement, const.savings_dividend)
    logger.debug(f"params: {params}")
    cur.execute(exec_str, params)
    current_savings_balance = cur.fetchone()[0]
    logger.debug(f"current_savings_balance: {current_savings_balance}")
    print(f"===============================================")
    print(f" current savings balance: ${current_savings_balance / 100:,.2f}")
    print(f"===============================================")

    # get date_paid
    dividend_date = utils.prompt_for_current_date("Date of dividend")
    # get amount
    dividend_amount = utils.prompt_for_amount("Amount of dividend")
    # prompt for notes ... 'Dep for Jan 2019' ... or similar
    note = f"Savings dividend"

    # enter into the activity log
    exec_str = f"""
        INSERT INTO activity (date, type, amount, note) 
        VALUES (?, ?, ?, ?)
    """
    params = (dividend_date, const.savings_dividend, dividend_amount, note)
    cur.execute(exec_str, params)

    # check the balance again
    exec_str = f"""
            SELECT SUM(amount)
            FROM activity 
            WHERE type = (?)
            OR type = (?)
            OR type = (?)
        """
    params = (const.savings_deposit_made, const.savings_disbursement, const.savings_dividend)
    cur.execute(exec_str, params)
    current_savings_balance = cur.fetchone()[0]
    logger.debug(f"current_savings_balance: {current_savings_balance}")
    print(f"===============================================")
    print(f" current savings balance: ${current_savings_balance / 100: ,.2f}")
    print(f"===============================================")

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    utils.init_logging("logs/savings_dividend.log")
    main()
