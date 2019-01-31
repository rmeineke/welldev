import logging
import sys
import sqlite3
import account
from lib import utils


def main():
    database = 'well.db'

    ASSESSMENT_PER_GALLON = 0.0025

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

    # insert into the transaction log
    cur.execute('INSERT INTO transactions_log (transaction_type, transaction_date, transaction_amount) VALUES (?, ?, ?)',
                (5, bill_date, pge_bill))

    # instantiate an obj for each of the accounts
    cur.execute("SELECT * FROM accounts")
    rows = cur.fetchall()

    acct_list = []
    total_usage = 0.0

    # each row('r') ... should represent an individual account
    for r in rows:
        acct_obj = account.Account(r['acct_id'], r['first_name'], r['last_name'], r['address'], r['reads_in'], ['master'])
        acct_list.append(acct_obj)

        # fetch the last two reading rows from the db
        rows = cur.execute('SELECT reading FROM readings WHERE account_id = {} ORDER BY reading_id DESC LIMIT 2'.format(r['acct_id']))
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
    savings_balance = utils.get_savings_balance(logger, database)
    logger.debug(f'savings_balance: {savings_balance}')

    assessment_total = 0
    for a in acct_list:
        logger.debug(f'\n\n{a.addr}')
        logger.debug(f'current_usage_percent: {a.current_usage_percent}')
        logger.debug(f'{(a.current_usage / total_usage) * 100}')
        logger.debug(f'{total_usage}')

        a.current_usage_percent = round((a.current_usage / total_usage) * 100, 2)
        logger.debug(f'current_usage_percent: {a.current_usage_percent:.2f}')
        logger.debug(f'pge_bill: {pge_bill}')
        logger.debug(f'a.current_usage_percent: {a.current_usage_percent}')

        # built-in round works properly here
        # print(f' >>>>>>>>>>>>>>>>> {round((pge_bill * a.current_usage_percent / 100),0)}')
        # print(f' >>>>>>>>>>>>>>>>> {int(pge_bill * a.current_usage_percent / 100)}')

        a.pge_bill_share = round((pge_bill * a.current_usage_percent / 100), 0)
        logger.debug(f'pge_bill_share: {a.pge_bill_share}')

        # write this share to the db - master_account table
        cur.execute('INSERT INTO master_account (acct_id, date, amount, notes) VALUES (?, ?, ?, ?)',
                    (a.acct_id, bill_date, a.pge_bill_share, 'PGE Bill Share'))

        # this should be moved outside ... no sense going through all
        # this if no assessment needed ...
        # move it outside and process as separate
        if savings_balance < 1000000:
            logger.debug(f'Assessment is due.')
            a.savings_assessment = int(round(a.current_usage * ASSESSMENT_PER_GALLON * 100, 0))
            logger.debug(f'Assessed: {a.savings_assessment}')
            # write this to the db
            cur.execute('INSERT INTO master_account (acct_id, date, amount, notes) VALUES (?, ?, ?, ?)',
                        (a.acct_id, bill_date, a.savings_assessment, 'Savings Assessment'))

            assessment_total += a.savings_assessment
            logger.debug(f'Bill total: {round(a.savings_assessment + a.pge_bill_share,2)}')
        else:
            logger.debug(f'No assessment needed.')

    assessment_total = int(round(assessment_total, 2))
    print(f'============================================================================')
    print(f'==> assessment_total: {assessment_total / 100:.2f}')
    print(f'============================================================================')
    cur.execute('INSERT INTO transactions_log (transaction_type, transaction_date, transaction_amount) '
                'VALUES (?, ?, ?)',
                (6, bill_date, assessment_total))

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
