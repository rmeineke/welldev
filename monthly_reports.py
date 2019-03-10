import logging
import sys
import sqlite3
from lib import utils
import account


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

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    last_two_reading_dates = utils.get_last_two_reading_dates(cur, logger)
    logger.debug(f"{last_two_reading_dates}")
    prev_month_reading_date = last_two_reading_dates[1]
    curr_month_reading_date = last_two_reading_dates[0]
    logger.debug(f"{prev_month_reading_date} ... {curr_month_reading_date}")

    acct_list = []
    cur.execute("SELECT * FROM accounts")
    rows = cur.fetchall()
    ttl_monthly_usage = 0
    for r in rows:
        # init the accounts
        logger.debug(f"\ninit an account ... add to acct list ... {r['last_name']} ... {r['acct_id']}")
        acct_obj = account.Account(r['acct_id'], r['first_name'], r['last_name'], r['address'], r['reads_in'], ['master'])
        acct_list.append(acct_obj)

        # get and set the previous balance
        prev_balance = utils.get_prev_balance(cur, acct_obj.acct_id, prev_month_reading_date, logger)
        acct_obj.prev_balance = prev_balance
        logger.debug(f"prev_balance: {prev_balance}")

        # check for any payments made
        payments_ttl = utils.get_payments_total(cur, acct_obj.acct_id, prev_month_reading_date, logger)
        if payments_ttl is None:
            payments_ttl = 0.0
        acct_obj.payments = payments_ttl
        logger.debug(f"payments_ttl: {payments_ttl}")

        # check for any other adjustments

        # new charges

        # show account balance


    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == "__main__":
    main()



    #
    #
    #     exec_str = f"""
    #         SELECT reading
    #         FROM readings
    #         WHERE account_id = {r['acct_id']}
    #         ORDER BY reading_id
    #         DESC
    #         LIMIT 2
    #     """
    #
    #     rows = cur.execute(exec_str)
    #     reading_list = []
    #     for row in rows:
    #         reading_list.append(row['reading'])
    #
    #     acct_obj.latest_reading = reading_list[0]
    #     current_reading = reading_list[0]
    #     acct_obj.previous_reading = reading_list[1]
    #     prev_reading = reading_list[1]
    #     logger.debug(f"prev: {prev_reading}")
    #     logger.debug(f"curr: {current_reading}")
    #     acct_obj.calculate_current_usage()
    #
    #     logger.debug(f"curr usage, gallons: {acct_obj.current_usage:.2f}")
    #     ttl_monthly_usage += acct_obj.current_usage_in_gallons
    #
    # exec_str = f"""
    #         SELECT transaction_amount
    #         FROM transactions_log
    #         WHERE transaction_type = 5
    #         ORDER BY transaction_date
    #         DESC
    #         LIMIT 1
    #    """
    # row = cur.execute(exec_str)
    # pge_bill = row.fetchone()
    # logger.debug(f"pge_bill: {pge_bill['transaction_amount']}")
    #
    # pct_sanity_chk = 0.0
    # for acct in acct_list:
    #     acct.calculate_current_usage_percent(ttl_monthly_usage)
    #     logger.debug(f"curr usage pct: {acct.current_usage_percent:10.2f}")
    #     pct_sanity_chk += acct.current_usage_percent
    #     acct.calculate_pge_bill_percent(pge_bill['transaction_amount'])
    #     logger.debug(f"pge_bill_share: {acct.pge_bill_share:10.2f}")
    #
    # print(f"\n")
    # logger.debug(f"pct_sanity_chk: {pct_sanity_chk:10.2f}")
    # logger.debug(f"ttl_monthly_usage: {ttl_monthly_usage}")
    # #
    # # exec_str = f"""
    # #     SELECT transaction_amount
    # #     FROM transactions_log
    # #     WHERE transaction_type = 5
    # # """
    # # row = cur.execute(exec_str)
    # # pge_bill = row.fetchone()
    # # logger.debug(f"pge_bill: {pge_bill['transaction_amount']}")