import logging
import sys
import sqlite3
from lib import utils
import account
from lib import constants


def main():
    database = "well.db"

    # set up for logging
    LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    if len(sys.argv) > 1:
        level_name = sys.argv[1]
        level = LEVELS.get(level_name, logging.NOTSET)
        logging.basicConfig(level=level)

    logger = logging.getLogger()
    logger.debug("Entering main")
    monthly_global_variables = {}

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    last_pge_bill_recd_date = utils.get_last_pge_bill_recd_date(cur, logger)
    last_pge_bill_recd_amount = utils.get_last_pge_bill_recd_amount(cur, logger)
    monthly_global_variables['last_pge_bill_recd_amount'] = last_pge_bill_recd_amount
    logger.debug(f"last_pge_bill_recd_date: {last_pge_bill_recd_date}")
    logger.debug(f"last_pge_bill_recd_amount: {last_pge_bill_recd_amount}")
    monthly_global_variables['last_pge_bill_recd_date'] = last_pge_bill_recd_date
    acct_list = []
    cur.execute("SELECT * FROM account")
    rows = cur.fetchall()
    ttl_monthly_usage = 0
    monthly_global_variables['ttl_monthly_usage'] = 0.0

    savings_balance = utils.get_savings_balance(logger, cur)
    # leave this in for testing:
    # savings_balance = 1000000
    if savings_balance < 1000000:
        monthly_global_variables['assessment_needed'] = True
    else:
        monthly_global_variables['assessment_needed'] = False

    dates = utils.get_last_two_reading_dates(cur, logger)
    start_date = dates[1]
    monthly_global_variables['start_date'] = start_date
    end_date = dates[0]
    monthly_global_variables['end_date'] = end_date
    readable_start_date = utils.make_date_readable(start_date)
    monthly_global_variables['readable_start_date'] = readable_start_date
    readable_end_date = utils.make_date_readable(end_date)
    monthly_global_variables['readable_end_date'] = readable_end_date

    for r in rows:
        if r['active'] == 'no':
            logger.debug(f"account {r['acct_id']} is INACTIVE")
            continue

        # init the accounts
        logger.debug(f"\ninit an account ... add to acct list ... {r['last_name']} ... {r['acct_id']}")
        acct_obj = account.Account(r['acct_id'], r['first_name'], r['last_name'], r['file_alias'], r['address'], r['reads_in'], ['master'])
        acct_list.append(acct_obj)

        # set readings
        utils.set_last_two_readings(cur, acct_obj, logger)

        # set current usage
        utils.set_current_usage(acct_obj, logger)

        # calculate total usage for the community
        ttl_monthly_usage = ttl_monthly_usage + acct_obj.current_usage
        monthly_global_variables['ttl_monthly_usage'] += acct_obj.current_usage

        logger.debug(f"ttl_monthly_usage>>>>>>>>>>>>: {ttl_monthly_usage}")

        # get and set the previous balance
        prev_balance = utils.get_prev_balance(cur, acct_obj.acct_id, last_pge_bill_recd_date, logger)
        if prev_balance is None:
            prev_balance = 0
        acct_obj.prev_balance = prev_balance
        logger.debug(f"prev_balance: {prev_balance}")

        # adjustments?
        adjustments = utils.get_adjustments(cur, acct_obj.acct_id, last_pge_bill_recd_date, logger)
        if adjustments is None:
            adjustments = 0
        acct_obj.adjustments = adjustments
        logger.debug(f"adjustments: {adjustments}")

        # fetch pge bill share
        pge_bill_share  = utils.get_pge_share(cur, acct_obj.acct_id, last_pge_bill_recd_date, logger)
        if pge_bill_share is None:
             pge_bill_share = 0
        acct_obj.pge_bill_share = pge_bill_share
        logger.debug(f"pge_bill_share: {pge_bill_share}")

        # fetch any savings assessments here

        # check for any payments made
        payments = utils.get_payments(cur, acct_obj.acct_id, last_pge_bill_recd_date, logger)
        if payments is None:
            payments = 0
        acct_obj.payments = payments
        logger.debug(f"payments: {payments}")

        # this is just new pge shares and assessments ...
        # new charges
        new_charges = utils.get_new_charges(cur, acct_obj.acct_id, last_pge_bill_recd_date, logger)
        if new_charges is None:
            new_charges = 0
        acct_obj.new_charges = new_charges
        logger.debug(f"new charges: {acct_obj.new_charges}")

        acct_obj.current_balance = acct_obj.prev_balance + acct_obj.adjustments + acct_obj.payments + acct_obj.new_charges

    logger.debug(f"---------------- ttl_monthly_usage: {ttl_monthly_usage}")
    logger.debug(f"------------------ {monthly_global_variables['ttl_monthly_usage']}")
    dates = utils.get_last_two_reading_dates(cur, logger)

    const = constants.Constants()
    exec_str = f"""
        SELECT *
        FROM activity
        WHERE (type = ? OR type = ? OR type = ?)
        AND
        (date >= ?)
    """
    params = (const.savings_deposit_made, const.savings_dividend,
              const.savings_disbursement, dates[1])
    rows = cur.execute(exec_str, params)
    savings_data_list = []
    for row in rows:
        logger.debug(f".................... {row['type']} - {row['date']} - {row['amount']} - {row['note']}")
        data_list = []
        if row['type'] == const.savings_deposit_made:
            data_list.append("Deposit made")
        elif row['type'] == const.savings_dividend:
            data_list.append("Dividend to account")
        data_list.append(row['date'])
        data_list.append(row['amount'] / 100)
        data_list.append(row['note'])
        savings_data_list.append(data_list)
    logger.debug(f"{savings_data_list}")
    # need to get the savings info outside of this loop ....
    # pass it in as a parameter ... otherwise we'll be hitting the
    # DB four times for the exact same information
    for acct in acct_list:
        utils.generate_pdf(cur, acct, monthly_global_variables, savings_data_list, start_date, readable_start_date, end_date, readable_end_date, logger)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == "__main__":
    main()
