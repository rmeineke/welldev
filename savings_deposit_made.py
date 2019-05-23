import logging
import sys
import sqlite3
from lib import utils
from lib import constants


def main():
    database = 'well.sqlite'

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
    if current_savings_balance is None:
        current_savings_balance = 0
    logger.debug(f"current_savings_balance: {current_savings_balance}")
    print(f"===============================================")
    print(f" current savings balance: ${current_savings_balance / 100:,.2f}")
    print(f"===============================================")

    # get date_paid
    deposit_date = utils.prompt_for_current_date(logger, "Date deposit made")
    # get amount
    deposit_amount = utils.prompt_for_amount(logger, "Amount of deposit")
    # prompt for notes ... 'Dep for Jan 2019' ... or similar
    note = utils.prompt_for_notes(logger, 'Notes for this deposit')

    exec_str = f"""
        INSERT INTO activity (date, type, amount, note) VALUES (?, ?, ?, ?)
    """
    params = (deposit_date, const.savings_deposit_made, deposit_amount, note)
    cur.execute(exec_str, params)

    # # get master acct id
    # exec_str = f"""
    #     SELECT acct_id
    #     FROM account
    #     WHERE master = "yes"
    # """
    # cur.execute(exec_str)
    # # fetchone ROW .... zeroeth item is the account number
    # master_acct_id = cur.fetchone()[0]
    # logger.debug(f'master_acct_id: {master_acct_id}')
    #
    # # get last assessment for the master acct
    # # select amount from activity where acct = 3 and type = 9;
    # exec_str = f"""
    #     SELECT amount
    #     FROM activity
    #     WHERE acct = (?)
    #     AND type = (?)
    #     ORDER BY date
    #     DESC
    #     LIMIT 1
    # """
    # params = (master_acct_id, const.savings_assessment)
    # cur.execute(exec_str, params)
    #
    # last_assessment_for_master = cur.fetchone()[0]
    # logger.debug(f"last_assessment_for_master: {last_assessment_for_master}")
    # # reverse the amount and write it back
    # last_assessment_for_master = last_assessment_for_master * -1
    # logger.debug(f"last_assessment_for_master: {last_assessment_for_master}")
    #
    # exec_str = f"""
    #     INSERT INTO activity (date, acct, type, amount, note)
    #     VALUES (?, ?, ?, ?, ?)
    # """
    # params = (deposit_date, master_acct_id, const.payment,
    #           last_assessment_for_master, "Payment on account (savings deposit)")
    # cur.execute(exec_str, params)

    exec_str = f"""
            SELECT SUM(amount)
            FROM activity 
            WHERE type = (?)
            OR type = (?)
            OR type = (?)
        """
    params = (const.savings_deposit_made, const.savings_disbursement, const.savings_dividend)
    print(f"{params}")
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
    main()
