import logbook
import sqlite3
import account
from lib import utils


def main():
    database = "well.sqlite"

    logger = logbook.Logger("percentages")

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    cur.execute("SELECT * FROM account")
    rows = cur.fetchall()

    acct_list = []
    total_usage = 0.0
    for r in rows:
        if r["active"] == "no":
            continue

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

        # fetch the last two reading rows from the db
        acct_id = r["acct_id"]
        rows = utils.fetch_last_two_reading(cur, acct_id)
        # need to collect them both in a list for further processing
        readings_list = []
        for row in rows:
            readings_list.append(row["reading"])
        logger.trace(f"reads in: {acct_obj.reads_in}")
        logger.trace(f"readings_list: {readings_list}")
        acct_obj.latest_reading = readings_list[0]
        acct_obj.previous_reading = readings_list[1]

        acct_obj.calculate_current_usage()
        logger.trace(f"current usage: {acct_obj.current_usage}")

        total_usage += acct_obj.current_usage
    logger.trace(f"total usage: {total_usage:.2f}")
    total_usage = round(total_usage, 2)
    logger.trace(f"total usage, rounded: {total_usage:.2f}")
    percents_total = 0
    for a in acct_list:
        a.current_usage_percent = round(a.current_usage / total_usage * 100, 2)
        print(f"{a.ln:20}...  {a.current_usage_percent:8.2f}%")
        logger.trace(f"{a.current_usage / total_usage * 100}")
        percents_total += a.current_usage_percent

    logger.trace(f"\n{'percents_total:':19} ... {percents_total:9.2f}%\n")

    # close the cursor and db
    cur.close()
    db.close()


if __name__ == "__main__":
    utils.init_logging("logs/percentages.log")
    main()
