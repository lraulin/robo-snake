import sqlite3
from pypika import Query, Table, Field
from common.constants import DB_FILE_NAME

TBL_CATEGORY = "category"
TBL_DIRECT_EXPRESS = "direct_express"
TBL_DIRECT_EXPRESS_CHANGE_LOG = "direct_express_change_log"
TBL_GROUP = "group"
EVERYTHING = "*"
HIDE = "Hide"


def get_cursor_and_con(db_name):
    con = sqlite3.connect(db_name)
    cursor = con.cursor()
    return cursor, con


def get_table_info(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    cols = cursor.fetchall()
    col_names = [col[1] for col in cols]
    primary_key = [col[1] for col in cols if col[-1] == 1][0]  # Assume one primary key
    return col_names, primary_key


def get_operation_counts(table_name, cursor):
    log_table_name = f"{table_name}_change_log"
    cursor.execute(f"SELECT operation, count FROM {log_table_name};")
    change_counts = cursor.fetchall()
    print(f"Change log for {table_name}:")
    print(change_counts)
    insert_count = [count for op, count in change_counts if op == "insert"][0]
    update_count = [count for op, count in change_counts if op == "update"][0]
    return insert_count, update_count


def upsert(table_name: str, records: list[tuple]) -> None:
    cursor, con = get_cursor_and_con(DB_FILE_NAME)
    initial_inserted, initial_updated = get_operation_counts(table_name, cursor)
    col_names, primary_key = get_table_info(cursor, table_name)

    num_cols = len(col_names)
    place_holders = ("?," * num_cols)[:-1]

    # Excluding the primary key for the update operation
    update_fields = [col for col in col_names if col != primary_key]
    update_clause = ", ".join(
        [f"{field} = excluded.{field}" for field in update_fields]
    )
    # Excluding the primary key and 'imported' column for the update operation
    update_fields = [col for col in col_names if col not in [primary_key, "imported"]]

    # Here's where we add our logic to conditionally update the 'imported' column.
    update_clause = ", ".join(
        [
            f"{field} = CASE WHEN excluded.imported <= IFNULL({table_name}.imported, 0) THEN {table_name}.{field} ELSE excluded.{field} END"
            for field in update_fields
        ]
    )

    # Adding specific logic for 'imported' column
    update_clause += f", imported = CASE WHEN excluded.imported <= IFNULL({table_name}.imported, 0) THEN {table_name}.imported ELSE excluded.imported END"

    sql = f"""INSERT INTO {table_name}
              VALUES ({place_holders})
              ON CONFLICT({primary_key})
              DO UPDATE SET {update_clause};"""

    print(sql)
    cursor.executemany(sql, records)
    con.commit()
    final_inserted, final_updated = get_operation_counts(table_name, cursor)
    print(f"Inserted {final_inserted - initial_inserted} records")
    print(f"Updated {final_updated - initial_updated} records")

    cursor.close()
    con.close()
    print(f"Successfully upserted {len(records)} records into {table_name}")


def insert_categories():
    csv = """Phone,Bills,Expense,
Utilities,Bills,Expense,
Amazon,Discretionary,Expense,
Big Toys,Discretionary,Expense,
Books,Discretionary,Expense,
Entertainment,Discretionary,Expense,
Games,Discretionary,Expense,
Home Improvements,Discretionary,Expense,
Meds & Suppliments,Discretionary,Expense,
Restaurants,Discretionary,Expense,
Subscriptions,Discretionary,Expense,
Classes,Kids,Expense,
Stuff,Kids,Expense,
Auto & Gas,Living,Expense,
Charity,Living,Expense,
Fees,Living,Expense,
Groceries,Living,Expense,
Healthcare,Living,Expense,
Misc,Living,Expense,
Mortgage,Living,Expense,
Repairs,Living,Expense,
Travel,Living,Expense,
Parking,Work,Expense,
Reimbursable,Work,Expense,Hide
Earned Interest,Income,Income,
Other Income,Income,Income,
Paycheck,Income,Income,
Tax Refund,Income,Income,
VA Benefits,Income,Income,
Transfer,Transfer Types,Transfer,Hide"""
    records = [tuple(line.split(",")) for line in csv.split("\n")]
    print(records)
    q = Query.from_(TBL_GROUP).select(EVERYTHING)
    sql = q.get_sql()
    print(sql)
    cur, con = get_cursor_and_con(DB_FILE_NAME)
    result = cur.execute(sql)
    group_dict = {
        group: {"id": id, "type": type} for id, group, type in result.fetchall()
    }
    print(group_dict)

    category_records = [
        (
            index + 1,
            category,
            group_dict[group]["id"],
            1 if hidden == HIDE else 0,
        )
        for index, (category, group, _, hidden) in enumerate(records)
    ]
    print(category_records)
    insert_q = Query.into(TBL_CATEGORY).insert(*category_records)
    print("SQL:")
    insert_sql = insert_q.get_sql()
    print(insert_sql)
    try:
        pass
        cur.execute(insert_sql)
        con.commit()
    except sqlite3.Error as error:
        print("Error occurred - ", error)

    finally:
        cur.close()
        con.close()
