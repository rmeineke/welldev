import logging
import sys
import json
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

    # open the file and read it in as json data
    with open('../data/accounts.json') as data_file:
        data = json.load(data_file)

    db = sqlite3.connect('{}'.format(db))
    cur = db.cursor()

    logger.debug('calling create_account_table')
    create_accounts_table(cur, logger)

    for acct in data["accounts"]:
        logger.debug('in the acct loop')
        logger.debug(acct)
        account_data_entry(cur, acct['first_name'], acct['last_name'], acct['address'], acct['reads_in'], acct['master'])

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


def create_accounts_table(c, logger):
    logger.debug('inside create_account_table')
    c.execute('DROP TABLE IF EXISTS accounts')
    c.execute('CREATE TABLE IF NOT EXISTS \
                accounts(acct_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                        first_name TEXT, \
                        last_name TEXT, \
                        address TEXT, \
                        reads_in TEXT, \
                        master TEXT)')


def account_data_entry(c, fn, ln, a, reads, master):
    c.execute('INSERT INTO accounts (first_name, last_name, address, reads_in, master) VALUES (?, ?, ?, ?, ?)',
              (fn, ln, str(a), reads, master))


if __name__ == '__main__':
    main()
