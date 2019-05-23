import logging
import sys
import sqlite3


def main():
    db = '../well.sqlite'

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

    db = sqlite3.connect('{}'.format(db))
    cur = db.cursor()

    logger.debug('calling create_savings_account_table')
    create_savings_account_table(cur, logger)
    cur.execute('INSERT INTO savings_account (date, amount, note) \
                VALUES ("2018-12-31", 912613, "Opening Balance")')
    cur.execute('INSERT INTO savings_account (date, amount, note) \
                    VALUES ("2019-01-30", 4240, "Jan 2019 assessment")')
    cur.execute('INSERT INTO savings_account (date, amount, note) \
                    VALUES ("2019-02-28", 5632, "Feb 2019 assessment")')
    cur.execute('INSERT INTO savings_account (date, amount, note) \
                    VALUES ("2019-03-19", 290, "Dividend to account")')
    db.commit()
    cur.close()
    db.close()


def create_savings_account_table(c, logger):
    logger.debug('inside create_savings_account_table')
    c.execute('DROP TABLE IF EXISTS savings_account')
    c.execute('CREATE TABLE IF NOT EXISTS \
                savings_account(transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                        date TEXT, \
                        amount INTEGER, \
                        note TEXT)')


def account_data_entry(c, date, amount, notes):
    c.execute('INSERT INTO savings_account (date, amount, note) VALUES (?, ?, ?)',
              (date, amount, notes))


if __name__ == '__main__':
    main()
