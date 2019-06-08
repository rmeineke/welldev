import sqlite3

import logbook
from lib import utils
from lib import constants

def main():
    fee_logger = logbook.Logger('main')
    const = constants.Constants()

    database = 'well.sqlite'
    fee_logger.notice('Connecting to the database')
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    fee_date: str = utils.prompt_for_current_date("Fee date")
    fee_logger.trace(f'fee_date: {fee_date}')
    fee_amount: int = utils.prompt_for_amount("Fee amount")
    fee_logger.trace(f'fee amount: {fee_amount}')
    qtr_share: int = int(round(fee_amount/4))
    fee_logger.trace(f'qtr_share (rounded): {qtr_share}')
    fee_note = utils.prompt_for_notes("Notes")
    fee_logger.trace(f'fee_note: {fee_note}')

    # enter this into the activity log prior to entering each
    # 1/4 share individually
    exec_str = f"""
                    INSERT INTO activity (date, type, amount, note)
                    VALUES (?, ?, ?, ?)
                """
    params = (fee_date, const.administrative_fee_received, fee_amount, fee_note)
    cur.execute(exec_str, params)

    exec_str = "SELECT * FROM account"
    cur.execute(exec_str)
    rows = cur.fetchall()
    for r in rows:
        if r["active"] == "no":
            fee_logger.trace(f"Account {r['acct_id']} currently INACTIVE")
            continue
        exec_str = f"""
            INSERT INTO activity (date, acct, type, amount, note) 
            VALUES (?,?,?,?,?)
        """
        params = (fee_date, r["acct_id"], const.administrative_fee_share, qtr_share, fee_note)
        cur.execute(exec_str, params)

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()


def init_logging(filename: str = None):
    level = logbook.TRACE
    if filename:
        logbook.TimedRotatingFileHandler(filename, level=level).push_application()
    else:
        logbook.StreamHandler(sys.stdout, level=level).push_application()
    msg = f"Logging initialized: level = {level}"

    logger = logbook.Logger('Startup')
    logger.notice(msg)


if __name__ == '__main__':
    init_logging('admin_fee.log')
    main()
