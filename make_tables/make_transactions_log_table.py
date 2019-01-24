#! /usr/bin/python3

import logging
import sys
import sqlite3


def main():
    db = '../well.db'

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
    logger.debug('Entering Main')

    db = sqlite3.connect(db)
    cur = db.cursor()

    logger.debug('calling create_transactions_log_table')
    create_transactions_log_table(cur, logger)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


def create_transactions_log_table(c, logger):
    logger.debug('inside create_transactions_log')
    c.execute('DROP TABLE IF EXISTS transactions_log')
    c.execute('CREATE TABLE IF NOT EXISTS transactions_log (transaction_id INTEGER PRIMARY KEY, acct_id INTEGER, transaction_type INTEGER, transaction_date DATE, transaction_amount INTEGER)')

    c.execute('INSERT INTO transactions_log (transaction_type, transaction_date, transaction_amount) VALUES (?, ?, ?)', (3, '2018-12-27', 0.00))


if __name__ == '__main__':
    main()
