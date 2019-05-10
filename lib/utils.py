import datetime
import os
import sqlite3
from shutil import copyfile
import fpdf
from datetime import datetime

from lib import constants


def generate_unique_pdf_filename(stub):
    count = 0
    fn = stub + '.pdf'
    while True:
        if os.path.exists(fn):
            count += 1
            fn = stub + "(" + str(count) + ").pdf"
        else:
            print(f"output_file: {fn}")
            return fn


def generate_pdf(cur, acct_obj, ttl_usage, savings_data_list, logger):
    logger.debug(f"entering generate_pdf")

    # let's get a few things set up here ...
    dt = datetime.now().strftime("%Y.%m.%d")
    stub = f"{acct_obj.file_alias}--{dt}"
    output_file = generate_unique_pdf_filename(stub)

    pdf = fpdf.FPDF('P', 'pt', 'Letter')
    pdf.add_page()

    pdf.set_font('Arial', 'B', 16)
    lh = pdf.font_size
    pdf.cell(0, 0, f"{acct_obj.fn} {acct_obj.ln}")
    pdf.ln(lh)
    pdf.cell(0, 0, f"{acct_obj.addr}")
    pdf.ln(lh)
    pdf.cell(0, 0, 'Aromas, CA  95004')
    pdf.ln(lh)
    pdf.ln(lh)
    epw = pdf.w - (2 * pdf.l_margin)
    col_width = epw / 5

    pdf.ln(lh)
    pdf.set_fill_color(220, 220, 220)

    # headers
    pdf.set_font('Courier', '', 10)
    pdf.cell(col_width, lh, f"Previous Balance", border="LTR", align="C")
    pdf.cell(col_width, lh, f"Payments", border="LTR", align="C")
    pdf.cell(col_width, lh, f"Adjustments", border="LTR", align="C")
    pdf.cell(col_width, lh, f"New Charges", border="LTR", align="C")
    pdf.cell(col_width, lh, f"Account Balance", border="LTR", align="C", fill=True)
    pdf.ln(lh)

    # data
    pdf.set_font('Courier', '', 10)
    pdf.cell(col_width, lh, f"{acct_obj.prev_balance / 100:.2f}", border='LBR', align='C')
    pdf.cell(col_width, lh, f"{acct_obj.payments / 100:.2f}", border='LBR', align='C')
    pdf.cell(col_width, lh, f"{acct_obj.adjustments / 100:.2f}", border='LBR', align='C')
    pdf.cell(col_width, lh, f"{acct_obj.new_charges / 100:.2f}", border='LBR', align='C')
    pdf.set_font('Courier', 'B', 12)
    pdf.cell(col_width, lh, f"{acct_obj.current_balance / 100:.2f}", border='LBR', align='C', fill=True)
    pdf.ln(lh)

    # usage
    pdf.set_font('Arial', 'B', 12)
    pdf.ln(pdf.font_size)
    lh = pdf.font_size

    # TODO: this needs to be moved out as well
    # fetching this 4 times !
    dates = get_last_two_reading_dates(cur, logger)

    pdf.ln()
    col_width = epw / 2
    pdf.cell(col_width, lh, f"Your usage:", border="B")
    pdf.set_font('Arial', '', 10)
    # TODO: make these dates human-readable
    pdf.cell(0, lh, f"{dates[1]} to {dates[0]}", border="B", align='R')
    pdf.ln(lh)
    pdf.ln(lh)
    col_width = epw / 4
    pdf.set_font('Arial', '', 12)
    lh = lh + 2
    pdf.cell(col_width, 0, f"Latest reading:")
    pdf.cell(col_width, 0, f"{acct_obj.latest_reading}", align='R')
    pdf.ln(lh)
    pdf.cell(col_width, 0, f"Previous reading:")
    pdf.cell(col_width, 0, f"{acct_obj.previous_reading}", align='R')
    pdf.ln(lh)
    pdf.cell(col_width, 0, f"Difference:")
    pdf.cell(col_width, 0, f"{acct_obj.latest_reading - acct_obj.previous_reading}", align="R")
    pdf.ln(lh)

    # TODO: bust this into an if/else for those that read in gallons vs.
    # cubic feet
    if acct_obj.reads_in == 'cubic feet':
        pdf.cell(col_width, 0, f"Usage (gallons -- {acct_obj.latest_reading - acct_obj.previous_reading} x 7.4805):")
        pdf.cell(col_width, 0, f"{acct_obj.current_usage:.2f}", align="R")
        pdf.ln(lh)
    else:
        pdf.cell(col_width, 0, f"Usage (gallons):")
        pdf.cell(col_width, 0, f"{acct_obj.current_usage:.2f}", align="R")
        pdf.ln(lh)

    pdf.cell(col_width, 0, f"Total well usage (gallons): ")
    pdf.cell(col_width, 0, f"{ttl_usage:.2f}", align="R")
    pdf.ln(lh)
    current_usage_percent = (round((acct_obj.current_usage / ttl_usage), 4) * 100)
    pdf.cell(col_width, 0, f"Current usage percent: ")
    pdf.cell(col_width, 0, f"{current_usage_percent:.2f}%", align="R")
    pdf.ln(lh)


    pdf.set_font('Arial', 'B', 12)
    lh = pdf.font_size
    pdf.ln(lh)
    pdf.cell(0, lh, f"Your account activity:", border="B")
    pdf.ln(lh)

    pdf.set_font('Arial', 'B', 12)
    lh = pdf.font_size
    pdf.ln(lh)
    pdf.cell(0, lh, f"Savings account activity:", border="B")
    pdf.ln(lh)
    pdf.ln(lh)
    pdf.set_font('Arial', '', 12)
    for item in savings_data_list:
        col_width = epw / 3
        pdf.cell(col_width, 0, f"{item[1]} {item[0]}")
        pdf.cell(col_width, 0, f"{item[2]}", align='R')
        pdf.cell(col_width, 0, f"{item[3]}")
        pdf.ln(lh + 2)

    bal = get_savings_balance(logger, cur)
    bal = bal / 100
    pdf.ln(lh)
    pdf.cell(col_width, 0, f"Current savings account balance:")
    pdf.set_font('Arial', 'BI', 12)
    pdf.cell(0, 0, f" ${bal:.2f}")
    #
    # const = constants.Constants()
    # exec_str = f"""
    #     SELECT *
    #     FROM activity
    #     WHERE (type = ? OR type = ? OR type = ?)
    #     AND
    #     (date >= ?)
    # """
    # params = (const.savings_deposit_made, const.savings_dividend,
    #           const.savings_disbursement, dates[1])
    # rows = cur.execute(exec_str, params)
    # for row in rows:
    #     logger.debug(f".................... {row['date']} - {row['amount']}")
    # footers .............................................

    # 716 is as low as i can get this
    # without pushing to the next page
    pdf.set_y(716)
    pdf.set_font('Arial', 'i', 8)
    col_width = epw / 8
    pdf.ln()
    pdf.cell(col_width, 0, f"Google Pay:")
    pdf.cell(col_width, 0, f"rmeineke@gmail.com")
    pdf.ln(lh - 3)
    pdf.cell(col_width, 0, f"PayPal:")
    pdf.cell(col_width, 0, f"www.paypal.me/Rmeineke")
    pdf.cell(0, 0, "Questions or comments to: rmeineke@gmail.com", align='R')
    pdf.ln(lh - 3)
    pdf.cell(col_width, 0, f"Venmo:")
    pdf.cell(col_width, 0, f"www.venmo.com/Rmeineke")
    generated_str = f"File generated: {dt}"
    pdf.cell(0, 0, generated_str, align='R')

    # TODO: add generate at / by rsm message at the bottom

    # write the file
    pdf.output(output_file, 'F')
    # TODO: put a copy of the file in the backup folder

    logger.debug(f"leaving generate_pdf")


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
        WHERE account_id = ?
        ORDER BY reading_id
        DESC
        LIMIT 2
    """
    params = (acct_id, )
    rows = cur.execute(exec_str, params)
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
        SELECT date
        FROM reading_date
        ORDER BY date
        DESC 
        LIMIT 2
    """
    rows = cur.execute(exec_str)
    dates = []
    for row in rows:
        dates.append(row['date'])
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
    params = (acct_id, const.payment_received, date)
    # logger.debug(f"{exec_str}")
    row = cur.execute(exec_str, params)
    return row.fetchone()[0]


def get_pge_share(cur, acct_id, date, logger):
    const = constants.Constants()
    logger.debug(f"{acct_id} -- {date}")
    exec_str = f"""
        SELECT amount
        FROM activity
        WHERE acct = ?
        AND type = ?
        AND date >= ?
    """
    params = (acct_id, const.pge_bill_share, date)
    row = cur.execute(exec_str, params)
    logger.debug(f"{row}")
    return row.fetchone()[0]


def set_last_two_readings(cur, acct_obj, logger):
    # select reading from reading where account_id = 4 order by reading desc limit 2;
    exec_str = f"""
                SELECT reading
                FROM reading
                WHERE account_id = ?
                ORDER BY reading
                DESC
                LIMIT 2
            """
    params = (acct_obj.acct_id,)
    rows = cur.execute(exec_str, params)
    readings = []
    for row in rows:
        logger.debug(f"reading: {row['reading']}")
        readings.append(row['reading'])
    logger.debug(readings)
    acct_obj.latest_reading = readings[0]
    acct_obj.previous_reading = readings[1]
    pass


def set_current_usage(acct_obj, logger):
    const = constants.Constants()
    usage = acct_obj.latest_reading - acct_obj.previous_reading
    logger.debug(f"raw usage: {usage} -- {acct_obj.reads_in}")
    if acct_obj.reads_in == 'cubic feet':
        usage = round((usage * const.gallons_per_cubic_foot), 2)
    logger.debug(f"CONVERTED usage: {usage:.2f}")
    acct_obj.current_usage = usage


def set_current_usage_percent(acct, ttl_usage):
    pass

