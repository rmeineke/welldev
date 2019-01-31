import datetime
import os
import sqlite3
from shutil import copyfile


def backup_file(logger, fn):
    logger.debug('entering backup_file')
    backup_directory = './backups'
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)

    dt = datetime.datetime.now().strftime('%Y.%m.%d_%H.%M.%S')

    new_filename = os.path.join(backup_directory, dt + '__' + fn)
    logger.debug(f'backing up to: {new_filename}')
    copyfile(fn, new_filename)


def prompt_for_amount(logger, prompt):
    logger.debug('entering get_amount()')
    while 1:
        try:
            amt = input(f"{prompt}: $")

            # amt = round(float(amt) * 100, 2)
            # print(f'{amt}')
            #


            logger.debug(f'get_amount() input is: {amt}')
            # "{:.2f}".format(float(amt))
            amt = int(float(amt) * 100)
            logger.debug(f'get_amount() is going to return: {amt}')
            return amt
        except ValueError as e:
            logger.debug(e)
            print('Bad amount ... try again.')


def prompt_for_current_date(logger, prompt):
    logger.debug('entering prompt_for_current_date')
    while 1:
        try:
            reading_date = input("{}: ".format(prompt))
            date_obj = datetime.datetime.strptime(reading_date, '%m/%d/%Y')
            return datetime.datetime.strftime(date_obj, '%Y-%m-%d')
        except ValueError:
            print('Bad date ... try again.')


def prompt_for_notes(logger, prompt):
    logger.debug('entering prompt_for_notes')

    input_str = ''
    while 1:
        response = input("{} [q to quit]: ".format(prompt))
        if response == 'q':
            break
        input_str += response
    return input_str.strip()


def prompt_for_account(logger, prompt, cur):
    # get the account list
    cur.execute('SELECT * FROM accounts')
    rows = cur.fetchall()
    acct_list = []
    for r in rows:
        print('{}: {}'.format(r[0], r[2]))
        acct_list.append(r[0])

    while True:
        acct = input('{}: '.format(prompt))
        if int(acct) in acct_list:
            return acct


def get_savings_balance(logger, db):
    # this is way neater than what follows
    logger.debug('Entering get_savings_balance()')
    row = cur.execute("SELECT sum(amount) FROM savings_account")
    cur_balance = row.fetchone()[0]
    return cur_balance


def get_savings_balance(logger, db):
    logger.debug('Entering get_savings_balance()')
    savings_balance = 0

    db = sqlite3.connect(db)
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.execute("SELECT amount FROM savings_account")
    rows = cur.fetchall()
    logger.debug(rows)

    for row in rows:
        savings_balance += row['amount']

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()

    return savings_balance


def get_balance_from_transaction_log(db, logger):
    db = sqlite3.connect(db)
    cur = db.cursor()
    row = cur.execute("SELECT SUM(transaction_amount) FROM transactions_log WHERE transaction_type = 4 OR transaction_type = 5 OR transaction_type = 6  OR transaction_type = 7")
    cur_balance = row.fetchone()[0]
    cur.close()
    db.close()
    return cur_balance
