import logging
import sys
import sqlite3
import account


def main():
    database = 'well.db'

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

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    cur.execute('SELECT * FROM accounts')
    rows = cur.fetchall()
    logger.debug(rows)

    acct_list = []
    total_usage = 0.0

    for r in rows:
        acct_obj = account.Account(r['acct_id'], r['first_name'], r['last_name'], r['address'], r['reads_in'],
                                   r['master'])
        acct_list.append(acct_obj)

        # fetch the last two reading rows from the db
        rows = cur.execute(
            'SELECT reading FROM readings WHERE account_id = {} ORDER BY reading_id DESC LIMIT 2'.format(r['acct_id']))
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

        logger.debug(f'reads in: {acct_obj.reads_in} .. prev reading: {acct_obj.previous_reading}')
        total_usage += acct_obj.current_usage


    total_usage = round(total_usage, 2)
    logger.debug(f'total usage: {total_usage}')
    percents_total = 0
    for a in acct_list:
        a.current_usage_percent = round(a.current_usage / total_usage * 100, 2)
        print(f'{a.ln}: {a.current_usage_percent}')
        percents_total += a.current_usage_percent

    print(f'percents_total: {percents_total}')
    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()
