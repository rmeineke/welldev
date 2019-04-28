import datetime
import os
import sqlite3
from shutil import copyfile
from lib import constants


def backup_file(logger, fn):
    logger.debug("entering backup_file")
    backup_directory = "./backups"
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)

    dt = datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")

    new_filename = os.path.join(backup_directory, dt + "__" + fn)
    logger.debug(f"backing up to: {new_filename}")
    copyfile(fn, new_filename)


def prompt_for_amount(logger, prompt):
    logger.debug("entering get_amount()")
    while 1:
        try:
            amt = input(f"{prompt}: $")
            logger.debug(f"get_amount() input is: {amt}")
            logger.debug(f"amt: {amt}")
            logger.debug(f"float(amt): {float(amt)}")
            logger.debug(f"float(amt) * 100: {float(amt) * 100}")
            logger.debug(f"round float(amt) * 100: {round(float(amt) * 100, 0)}")
            amt = int(round(float(amt) * 100, 0))
            logger.debug(f"get_amount() is going to return: {amt}")
            return amt
        except ValueError as e:
            logger.debug(e)
            print("Bad amount ... try again.")


def prompt_for_current_date(logger, prompt):
    logger.debug("entering prompt_for_current_date")
    while 1:
        try:
            reading_date = input(f"{prompt}: ")
            # ................................................ 01/24/2019
            date_obj = datetime.datetime.strptime(reading_date, "%m/%d/%Y")
            # ......................................... 2019-01-24
            return datetime.datetime.strftime(date_obj, "%Y-%m-%d")
        except ValueError:
            print("Bad date ... try again.")


def prompt_for_notes(logger, prompt):
    logger.debug("entering prompt_for_notes")

    input_str = ""
    while 1:
        response = input("{} [q to quit]: ".format(prompt))
        if response == "q":
            break
        input_str += response
    return input_str.strip()


def prompt_for_account(logger, prompt, cur):
    # get the account list
    cur.execute("SELECT * FROM account")
    rows = cur.fetchall()
    acct_list = []
    for r in rows:
        print(f"{r[0]}: {r[2]}")
        acct_list.append(r[0])

    while True:
        acct = input(f"{prompt}: ")
        if int(acct) in acct_list:
            return acct

#
# def get_savings_balance(logger, db):
#     # this is way neater than what follows
#     logger.debug("Entering get_savings_balance()")
#     row = cur.execute("SELECT sum(amount) FROM savings_account")
#     cur_balance = row.fetchone()[0]
#     return cur_balance


def get_savings_balance(logger, cur):
    logger.debug('Entering get_savings_balance()')
    exec_str = f"""
        SELECT SUM(amount)
        FROM activity 
        WHERE type = (?)
        OR type = (?)
        OR type = (?)
    """
    const = constants.Constants()
    params = (const.savings_deposit_made, const.savings_disbursement, const.savings_dividend)
    row = cur.execute(exec_str, params)
    cur_balance = row.fetchone()[0]
    return cur_balance


def print_savings_account_balance(logger, cur):
    logger.debug('Entering print_savings_account_balance()')
    exec_str = f"""
            SELECT SUM(amount)
            FROM activity 
            WHERE type = (?)
            OR type = (?)
            OR type = (?)
        """
    const = constants.Constants()
    params = (const.savings_deposit_made, const.savings_disbursement, const.savings_dividend)
    row = cur.execute(exec_str, params)
    print(f"savings account balance: {(row.fetchone()[0] / 100):9.2f}")


def print_main_account_balance(logger, cur):
    logger.debug('Entering print_main_account_balance()')
    exec_str = f"""
            SELECT SUM(amount)
            FROM activity 
            WHERE type = (?)
            OR type = (?)
            OR type = (?)
            OR type = (?)
        """
    const = constants.Constants()
    params = (const.pge_bill_received, const.pge_bill_paid, const.savings_assessment, const.savings_deposit_made)
    row = cur.execute(exec_str, params)
    print(f"This figure should be close to 0:")
    print(f"main account balance: {(row.fetchone()[0] / 100):12.2f}")

def get_last_reading_date(logger, cur):
    exec_str = """
    SELECT reading_date FROM reading_dates ORDER BY reading_date DESC LIMIT 1
    """
    row = cur.execute(exec_str)
    return row.fetchone()[0]


def get_balance_from_transaction_log(db, logger):
    logger.debug("Entering get_balance_from_transaction_log")
    db = sqlite3.connect(db)
    cur = db.cursor()
    row = cur.execute(
        "SELECT SUM(transaction_amount) "
        "FROM transactions_log "
        "WHERE transaction_type = 4 OR transaction_type = 5 OR transaction_type = 6  OR transaction_type = 7"
    )
    cur_balance = row.fetchone()[0]
    cur.close()
    db.close()
    return cur_balance


def print_transaction_log_balance(cur, logger):
    logger.debug('Entering get_transaction_log_balance()')

    exec_str = f"""
        SELECT SUM(transaction_amount) 
        FROM transactions_log 
        WHERE transaction_type = 4 
        OR transaction_type = 5 
        OR transaction_type = 6 
        OR transaction_type = 7
    """

    row = cur.execute(exec_str)
    logger.debug(f'row: {row}')
    cur_balance = row.fetchone()[0]
    print(f'transaction log balance: {cur_balance / 100:9.2f}')


def print_master_account_balance(cur, logger):
    logger.debug('Entering get_master_account_balance()')

    exec_str = f"""
    SELECT sum(amount) FROM master_account
    """

    row = cur.execute(exec_str)
    cur_balance = row.fetchone()[0]
    print(f'\nmaster account balance: {cur_balance / 100:10.2f}')


def print_account_balances(logger, cur):
    logger.debug('Entering get_account_balances')
    # loop through and get acct ids
    # then get each balance and return

    exec_str = f"""
        SELECT acct_id, last_name, active 
        FROM account
    """
    logger.debug(f"{exec_str}")
    cur.execute(exec_str)
    rows = cur.fetchall()
    for r in rows:
        if r['active'] == 'no':
            logger.debug(f"account {r['acct_id']} is inactive")
            continue

        exec_str = f"""
            SELECT SUM(amount) 
            FROM activity
            WHERE acct = (?)
        """
        params = (r['acct_id'], )
        bal_row = cur.execute(exec_str, params)
        bal = bal_row.fetchone()[0]
        if bal is None:
            bal = 0
        print(f'{r["acct_id"]} -- {r["last_name"]:10} ....... {(bal / 100):>10,.2f}')


def fetch_last_two_reading(cur, acct_id, logger):
    exec_str = f"""
        SELECT reading
        FROM reading
        WHERE account_id = {acct_id}
        ORDER BY reading_id
        DESC
        LIMIT 2
    """
    rows = cur.execute(exec_str)
    return rows


def get_last_pge_bill_recd_date(cur, logger):
    logger.debug(f"entering get_last_pge_bill_recd_date")
    const = constants.Constants()

    exec_str = f"""
        SELECT date
        FROM activity
        WHERE type = (?)
        ORDER BY date
        DESC
    """
    params = (const.pge_bill_received, )
    cur.execute(exec_str, params)
    row = cur.fetchone()
    return row['date']

def get_last_two_reading_dates(cur, logger):
    logger.debug(f"entering get_last_two_reading_dates")
    exec_str = f"""
        SELECT reading_date
        FROM reading_dates
        ORDER BY reading_date
        DESC 
        LIMIT 2
    """
    rows = cur.execute(exec_str)
    dates = []
    for row in rows:
        dates.append(row['reading_date'])
    logger.debug(f"get_last_two_reading_dates ... returning: {dates}")
    return dates


def get_prev_balance(cur, acct_id, date, logger):
    """this needs altering to use the date of the last
    pge bill recd"""
    exec_str = f"""
        SELECT SUM(amount)
        FROM activity
        WHERE acct = ?
        AND date < ?
    """
    params = (acct_id, date)
    # logger.debug(f"{exec_str}")
    row = cur.execute(exec_str, params)
    return row.fetchone()[0]
#
# 12||4|2019-02-27|-2800
# 13|3|3|2019-02-27|-829
# 14||7|2019-02-28|-5632
# 15|3|3|2019-02-28|-1666
# sqlite> select sum(amount) from master__account where acct_id = 1;
# Error: no such table: master__account
# sqlite> select sum(amount) from master_account where acct_id = 1;
# 1746
# sqlite> select sum(amount) from master_account where acct_id = 4;
# 4115
# sqlite> select sum(amount) from master_account where acct_id = 4 and date <= '2019-01-27';
# 0
# sqlite> select sum(amount) from master_account where acct_id = 4 and date <= '2019-01-28';
# 1847
# sqlite>


def get_new_charges(cur, acct_id, date, logger):
    const = constants.Constants()

    exec_str = f"""
        SELECT SUM(amount)
        FROM activity
        WHERE acct = ?
        AND type IN (?, ?)
        AND date >= ?
    """
    params = (acct_id, const.pge_bill_share, const.savings_assessment, date)
    row = cur.execute(exec_str, params)
    return row.fetchone()[0]


def get_adjustments(cur, acct_id, date, logger):
    const = constants.Constants()
    exec_str = f"""
            SELECT SUM(amount)
            FROM activity
            WHERE acct = ?
            AND type = ?
            AND date >= ?
        """
    params = (acct_id, const.account_adjustment, date)
    row = cur.execute(exec_str, params)
    return row.fetchone()[0]


def get_payments(cur, acct_id, date, logger):
    const = constants.Constants()

    exec_str = f"""
        SELECT SUM(amount)
        FROM activity
        WHERE acct = ?
        AND type = ?
        AND date >= ?
    """
    params = (acct_id, const.payment, date)
    # logger.debug(f"{exec_str}")
    row = cur.execute(exec_str, params)
    return row.fetchone()[0]

# select sum(transaction_amount) from transactions_log where acct_id = 1 and transaction_type = 3 and transaction_date >= '2018-01-01';