#! /usr/bin/python3

import logging
import sys
import sqlite3
from lib import utils


def get_acct_balance(acct, cur):
    row = cur.execute("SELECT sum(amount) from master_account WHERE acct_id = {}".format(acct))
    bal = row.fetchone()[0]
    return bal / 100


def main():
    db = 'well.db'

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
    logger.debug('payment_made')
    logger.debug('Entering main')

    db = sqlite3.connect('{}'.format(db))
    cur = db.cursor()

    acct = utils.prompt_for_account(logger, 'Please choose an account', cur)
    date = utils.prompt_for_current_date(logger, 'Payment date')

    # fetch amount and flip the sign
    amt = utils.get_amount(logger, 'Payment amount')
    logger.debug(f'get_amount just returned this: {amt}')
    amt *= -1

    # cobble together the account note
    notes = 'Payment on account. Check #'
    notes += utils.prompt_for_notes(logger, 'Check number')
    notes += '.'

    logger.debug(date)
    logger.debug(amt)
    logger.debug(acct)
    logger.debug(notes)

    # fetch balance and display
    cur_balance = get_acct_balance(acct, cur)
    print(f'\n\nCurrent balance:\t{cur_balance:.2f}')

    # insert the account
    cur.execute('INSERT INTO master_account (acct_id, date, amount, notes) VALUES (?, ?, ?, ?)', (acct, date, amt, notes))

    # insert into the transaction log
    cur.execute("INSERT INTO transactions_log (acct_id, transaction_type, transaction_date, transaction_amount) "
                "VALUES (?, ?, ?, ?)", (acct, 3, date, amt))

    # fetch updated balance and display
    cur_balance = get_acct_balance(acct, cur)
    print(f'Updated balance:\t{cur_balance:.2f}')

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == '__main__':
    main()



"""
root:payment_made
DEBUG:root:Entering main
1: Schultz
2: Cain
3: Meineke
4: Olivares
Please choose an account: 4
DEBUG:root:entering prompt_for_current_date
Payment date: 01/19/2017
DEBUG:root:entering get_amount()
Payment amount: $100.31
DEBUG:root:entering prompt_for_notes
Check number [q to quit]: 2881
Check number [q to quit]: q
DEBUG:root:2017-01-19
DEBUG:root:-10031
DEBUG:root:4
DEBUG:root:Payment on account. Check #2881.


Current balance:	41.31
Updated balance:	-59.0
robertm@Sys76:~/programming/welldev$



k number [q to quit]: 10
Check number [q to quit]: q
DEBUG:root:2019-01-21
DEBUG:root:-451
DEBUG:root:1
DEBUG:root:Payment on account. Check #10.


Current balance:        4.52
Updated balance:        0.01
(welldev-qLYElE8t) robertm@sys76:~/programming/welldev$ 


"""