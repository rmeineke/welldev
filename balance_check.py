import sqlite3
from lib import utils


def main():
    database = 'well.sqlite'

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    print(f"")
    utils.print_account_balances(cur)
    print(f"")
    utils.print_savings_account_balance(cur)
    print(f"")

    # close the cursor and db
    cur.close()
    db.close()


if __name__ == '__main__':
    utils.init_logging('balance_check.log')
    main()
