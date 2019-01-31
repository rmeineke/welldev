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

    logger.debug('calling create_transaction_table')
    create_transaction_types_table(cur, logger)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


def create_transaction_types_table(c, logger):
    logger.debug('inside create_transaction_types')
    c.execute('DROP TABLE IF EXISTS transaction_types')
    c.execute('CREATE TABLE IF NOT EXISTS \
                transaction_types(type_id INTEGER PRIMARY KEY, transaction_type TEXT)')

    c.execute('INSERT INTO transaction_types (transaction_type) VALUES (?)', ("Administrative Fee Paid",))
    c.execute('INSERT INTO transaction_types (transaction_type) VALUES (?)', ("Administrative Fee Received",))
    c.execute('INSERT INTO transaction_types (transaction_type) VALUES (?)', ("Payment Received",))
    c.execute('INSERT INTO transaction_types (transaction_type) VALUES (?)', ("PGE Bill Paid",))
    c.execute('INSERT INTO transaction_types (transaction_type) VALUES (?)', ("PGE Bill Received",))
    c.execute('INSERT INTO transaction_types (transaction_type) VALUES (?)', ("Savings Assessment",))
    c.execute('INSERT INTO transaction_types (transaction_type) VALUES (?)', ("Savings Deposit",))
    c.execute('INSERT INTO transaction_types (transaction_type) VALUES (?)', ("Savings Disbursement",))
    c.execute('INSERT INTO transaction_types (transaction_type) VALUES (?)', ("Monthly Reading",))
    c.execute('INSERT INTO transaction_types (transaction_type) VALUES (?)', ("Account Adjustment",))


if __name__ == '__main__':
    main()
