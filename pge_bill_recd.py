import logging
import sys
import sqlite3
import account
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

    # make sure this gets backed up prior to any
    # writing of the db
    utils.backup_file(logger, database)
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # prompt for amount of the bill .. and date
    bill_date = utils.prompt_for_current_date(logger, 'Date of bill')
    pge_bill = float(utils.prompt_for_amount(logger, 'PGE bill amount'))
    logger.debug(f'pge_bill: {int(pge_bill)}')

    const = constants.Constants()
    exec_str = f"""
        INSERT INTO activity (date, type, amount, note) 
        VALUES (?, ?, ?, ?)
    """
    params = (bill_date, const.pge_bill_received, pge_bill, "PGE bill received")
    cur.execute(exec_str, params)

    # instantiate an obj for each of the accounts
    cur.execute("SELECT * FROM account")
    rows = cur.fetchall()

    acct_list = []
    total_usage = 0.0

    # each row('r') ... should represent an individual account
    for r in rows:
        if r['active'] == 'no':
            logger.debug(f"Account {r['acct_id']} currently INACTIVE")
            continue
        acct_obj = account.Account(r['acct_id'], r['first_name'], r['last_name'], r['file_alias'], r['address'], r['reads_in'], r['master'])
        acct_list.append(acct_obj)

        # fetch the last two reading rows from the db
        query: str = f"""
            SELECT reading 
            FROM reading
            WHERE account_id = (?)
            ORDER BY reading_id 
            DESC LIMIT 2
        """
        params = (r['acct_id'], )
        rows = cur.execute(query, params)

        # near as I can tell this returns a row for each line of data found
        # the row is a list of selected items .... so 'reading' is the
        # zeroeth item ...
        #
        # need to collect them both in a list for further processing
        readings_list = []
        for row in rows:
            readings_list.append(row['reading'])  # this retrieval by name seems to be fine

        logger.debug(f'readings_list: {readings_list}')
        acct_obj.latest_reading = readings_list[0]
        acct_obj.previous_reading = readings_list[1]

        acct_obj.calculate_current_usage()
        logger.debug(f'current usage: {acct_obj.current_usage}')

        logger.debug(f'{acct_obj.reads_in} .. {acct_obj.previous_reading}')
        total_usage += acct_obj.current_usage
    total_usage = round(total_usage, 2)
    logger.debug(f'total usage: {total_usage}')

    # a balance less than $10k should trigger an assessment
    # in the upcoming for loop
    savings_balance = utils.get_savings_balance(logger, cur)
    logger.debug(f'savings_balance: {savings_balance}')

    assessment_total = 0
    for acct in acct_list:
        logger.debug(f'\n\n{acct.addr}')

        logger.debug(f'current_usage_percent (b4 calculation): {acct.current_usage_percent}')
        logger.debug(f'current_usage_percent: {(acct.current_usage / total_usage) * 100}')
        logger.debug(f'total_usage: {total_usage}')

        acct.current_usage_percent = round((acct.current_usage / total_usage) * 100, 2)
        logger.debug(f'current_usage_percent (rounded): {acct.current_usage_percent:.2f}')
        logger.debug(f'pge_bill: {int(pge_bill)}')
        logger.debug(f'a.current_usage_percent: {acct.current_usage_percent}')

        acct.pge_bill_share = round((pge_bill * acct.current_usage_percent / 100), 0)
        logger.debug(f'pge_bill_share: {int(acct.pge_bill_share)}')

        exec_str = f"""
            INSERT INTO activity (date, acct, type, amount, note) 
            VALUES (?, ?, ?, ?, ?)
        """
        params = (bill_date, acct.acct_id, const.pge_bill_share, acct.pge_bill_share, "PGE bill share")
        cur.execute(exec_str, params)

        # this should be moved outside ... no sense going through all
        # this if no assessment needed ...
        # move it outside and process as separate
        if savings_balance < 1000000:
            logger.debug(f'Assessment is due.')
            acct.savings_assessment = int(round(acct.current_usage * const.assessment_per_gallon * 100, 0))
            logger.debug(f'Assessed: {acct.savings_assessment}')

            # write this to the db
            exec_str = f"""
                INSERT INTO activity (date, acct, type, amount, note) 
                VALUES (?, ?, ?, ?, ?)
            """
            params = (bill_date, acct.acct_id, const.savings_assessment, acct.savings_assessment, 'Savings assessment')
            cur.execute(exec_str, params)

            assessment_total += acct.savings_assessment
            logger.debug(f'Bill total: {int(round(acct.savings_assessment + acct.pge_bill_share, 2))}')
        else:
            logger.debug(f'No assessment needed.')

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
