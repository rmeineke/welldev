import logbook
import sqlite3
from lib import utils
from lib import constants


def main():
    logger = logbook.Logger('savings_dep')
    database = 'well.sqlite'

    utils.backup_file(database)
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    const = constants.Constants()
    exec_str = f"""
            SELECT SUM(amount)
            FROM (SELECT amount 
            FROM activity 
            WHERE type = (?)
            ORDER BY date
            DESC
            LIMIT 4)
        """
    params = (const.savings_assessment, )
    logger.trace(f"params: {params}")
    cur.execute(exec_str, params)
    last_assessment_ttl = cur.fetchone()[0]
    last_assessment_ttl = last_assessment_ttl / 100
    print(f"===============================================")
    print(f" last assessments totaled: ${last_assessment_ttl:.2f}")

    exec_str = f"""
        SELECT SUM(amount)
        FROM activity 
        WHERE type = (?)
        OR type = (?)
        OR type = (?)
    """
    params = (const.savings_deposit_made, const.savings_disbursement, const.savings_dividend)
    logger.trace(f"params: {params}")
    cur.execute(exec_str, params)
    current_savings_balance = cur.fetchone()[0]
    if current_savings_balance is None:
        current_savings_balance = 0
    logger.trace(f"current_savings_balance: {current_savings_balance}")
    print(f"===============================================")
    print(f" current savings balance: ${current_savings_balance / 100:,.2f}")
    print(f"===============================================")

    # get date_paid
    deposit_date = utils.prompt_for_current_date("Date deposit made")
    # get amount
    deposit_amount = utils.prompt_for_amount("Amount of deposit")
    # prompt for notes ... 'Dep for Jan 2019' ... or similar
    note = utils.prompt_for_notes('Notes for this deposit')

    exec_str = f"""
        INSERT INTO activity (date, type, amount, note) VALUES (?, ?, ?, ?)
    """
    params = (deposit_date, const.savings_deposit_made, deposit_amount, note)
    cur.execute(exec_str, params)

    exec_str = f"""
            SELECT SUM(amount)
            FROM activity 
            WHERE type = (?)
            OR type = (?)
            OR type = (?)
        """
    params = (const.savings_deposit_made, const.savings_disbursement, const.savings_dividend)
    logger.trace(f"{params}")
    cur.execute(exec_str, params)
    current_savings_balance = cur.fetchone()[0]
    logger.trace(f"current_savings_balance: {current_savings_balance}")
    print(f"===============================================")
    print(f" current savings balance: ${current_savings_balance / 100: ,.2f}")
    print(f"===============================================")

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    utils.init_logging('logs/savings_dep.log')
    main()
