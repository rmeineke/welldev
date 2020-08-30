import sqlite3
import logbook
from lib import utils
import account
from lib import constants


def main():
    database = "well.sqlite"
    logger = logbook.Logger("reports")

    # this dictionary will hold the variables that are needed
    # to process each account's nothing activity
    # this is outside any loop so that the info only
    # has to be culled once ... rather than each time the
    # loop is run for each account
    monthly_global_variables = {}

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    last_pge_bill_recd_date = utils.get_last_pge_bill_recd_date(cur)
    logger.trace(f"last_pge_bill_recd_date: {last_pge_bill_recd_date}")
    monthly_global_variables["last_pge_bill_recd_date"] = last_pge_bill_recd_date

    last_pge_bill_recd_amount = utils.get_last_pge_bill_recd_amount(cur)
    logger.trace(f"last_pge_bill_recd_amount: {last_pge_bill_recd_amount}")
    monthly_global_variables["last_pge_bill_recd_amount"] = last_pge_bill_recd_amount

    monthly_global_variables["ttl_monthly_usage"] = 0.0

    savings_balance = utils.get_savings_balance(cur)

    # leave this in for testing:
    # savings_balance = 1000000
    if savings_balance < 1000000:
        monthly_global_variables["assessment_needed"] = True
    else:
        monthly_global_variables["assessment_needed"] = False

    # collect relevant dates
    dates = utils.get_last_two_reading_dates(cur)
    logger.trace(f"dates --> {dates}")
    start_date = dates[1]
    logger.trace(f"start_date --> {start_date}")
    monthly_global_variables["start_date"] = start_date
    end_date = dates[0]
    logger.trace(f"end_date --> {end_date}")

    monthly_global_variables["end_date"] = end_date
    readable_start_date = utils.make_date_readable(start_date)
    monthly_global_variables["readable_start_date"] = readable_start_date
    readable_end_date = utils.make_date_readable(end_date)
    monthly_global_variables["readable_end_date"] = readable_end_date

    monthly_global_variables["current_savings_balance"] = utils.get_savings_balance(cur)
    const = constants.Constants()
    exec_str = f"""
            SELECT *
            FROM activity
            WHERE (type = ? OR type = ? OR type = ?)
            AND (date > ?)
        """
    params = (
        const.savings_deposit_made,
        const.savings_dividend,
        const.savings_disbursement,
        monthly_global_variables["start_date"],
    )
    logger.trace(params)
    rows = cur.execute(exec_str, params)
    savings_data_list = []
    for row in rows:
        logger.trace(f"{row['type']} - {row['date']} - {row['amount']} - {row['note']}")
        data_list = []
        if row["type"] == const.savings_deposit_made:
            data_list.append("Deposit made")
        elif row["type"] == const.savings_dividend:
            data_list.append("Dividend to account")
        data_list.append(row["date"])
        data_list.append(row["amount"] / 100)
        data_list.append(row["note"])
        savings_data_list.append(data_list)
    logger.trace(f"{savings_data_list}")

    acct_list = []
    cur.execute("SELECT * FROM account")
    rows = cur.fetchall()

    for r in rows:
        logger.trace(
            f"======================================================================="
        )

        if r["active"] == "no":
            logger.trace(f"account {r['acct_id']} is INACTIVE")
            continue

        # init the accounts
        logger.trace(
            f"init an account ... add to acct list ... {r['last_name']} ... {r['acct_id']}"
        )
        acct_obj = account.Account(
            r["acct_id"],
            r["first_name"],
            r["last_name"],
            r["file_alias"],
            r["address"],
            r["reads_in"],
            r["master"],
        )
        acct_list.append(acct_obj)

        # set readings
        utils.set_last_two_readings(cur, acct_obj)

        # set current usage
        utils.set_current_usage(acct_obj)

        # calculate total usage for the community
        # ttl_monthly_usage = ttl_monthly_usage + acct_obj.current_usage
        monthly_global_variables["ttl_monthly_usage"] += acct_obj.current_usage

        # get and set the previous balance
        # TODO: i think this needs to use the latest reading date...
        logger.trace(f" * * * Setting the prev_balance")
        logger.trace(f"start_date: {start_date}")
        logger.trace(f" * * * Setting the prev_balance")
        logger.trace(
            f"get_prev_balance is going to use {monthly_global_variables['end_date']}"
        )
        prev_balance = utils.get_prev_balance(
            cur, acct_obj.acct_id, monthly_global_variables["start_date"]
        )
        if prev_balance is None:
            prev_balance = 0
        acct_obj.prev_balance = prev_balance
        logger.trace(f"prev_balance: {prev_balance}")

        # adjustments?
        adjustments = utils.get_adjustments(
            cur, acct_obj.acct_id, last_pge_bill_recd_date
        )
        if adjustments is None:
            adjustments = 0
        acct_obj.adjustments = adjustments
        logger.trace(f"adjustments: {adjustments}")

        # fetch pge bill share
        pge_bill_share = utils.get_pge_share(
            cur, acct_obj.acct_id, last_pge_bill_recd_date
        )
        if pge_bill_share is None:
            pge_bill_share = 0
        acct_obj.pge_bill_share = pge_bill_share
        logger.trace(f"pge_bill_share: {pge_bill_share}")

        # check for any payments made
        payments = utils.get_payments(
            cur, acct_obj.acct_id, monthly_global_variables["start_date"]
        )
        if payments is None:
            payments = 0
        acct_obj.payments = payments
        logger.trace(f"==========================================")
        logger.trace(f"payments: {payments}")
        logger.trace(f"==========================================")

        # this is just new pge shares and assessments and new fees...
        # new charges
        new_charges = utils.get_new_charges(
            cur, acct_obj.acct_id, monthly_global_variables["start_date"]
        )
        if new_charges is None:
            new_charges = 0
        acct_obj.new_charges = new_charges
        logger.trace(f"new charges: {acct_obj.new_charges}")

        acct_obj.current_balance = (
            acct_obj.prev_balance
            + acct_obj.adjustments
            + acct_obj.payments
            + acct_obj.new_charges
        )
    logger.trace(f"{monthly_global_variables['ttl_monthly_usage']}")

    for acct in acct_list:
        utils.generate_pdf(cur, acct, monthly_global_variables, savings_data_list)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


if __name__ == "__main__":
    utils.init_logging("logs/reports.log")
    main()
