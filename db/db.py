import sqlite3
from pypika import Query, Table, functions as fn
from common.constants import DB_FILE_NAME
from tabulate import tabulate

TBL_CATEGORY = "category"
TBL_DIRECT_EXPRESS = "direct_express"
TBL_DIRECT_EXPRESS_CHANGE_LOG = "direct_express_change_log"
TBL_GROUP = "group"
EVERYTHING = "*"
HIDE = "Hide"


class InvalidQueryException(Exception):
    pass


def open_db(db_name):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    return connection, cursor


def close_db(connection, cursor):
    cursor.close()
    connection.close()


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
    con, cursor = open_db(DB_FILE_NAME)
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


def db_read(query: Query) -> list:
    sql = query.get_sql()
    if not sql.strip().upper().startswith("SELECT"):
        raise InvalidQueryException("Provided query is not a SELECT query.")

    try:
        con, cursor = open_db(DB_FILE_NAME)
        cursor.execute(query.get_sql())
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(e)
        raise e
    finally:
        close_db(con, cursor)


def db_write(query: Query) -> None:
    sql = query.get_sql()
    if not (
        sql.strip().upper().startswith("INSERT")
        or sql.strip().upper().startswith("UPDATE")
        or sql.strip().upper().startswith("DELETE")
    ):
        raise InvalidQueryException(
            "Provided query is not a valid write query (INSERT, UPDATE, DELETE)."
        )

    try:
        con, cursor = open_db(DB_FILE_NAME)
        cursor.execute(query.get_sql())
        con.commit()
        print("Successfully executed query.")
    except Exception as e:
        print(e)
        raise e
    finally:
        close_db(con, cursor)


def column_max(table, column) -> int:
    q = Query.from_(table).select(fn.Max(table[column]))
    result = db_read(q)
    try:
        return result[0][0]
    except IndexError:
        return 0


def select_and_print_table(table_name):
    conn, cursor = open_db(DB_FILE_NAME)

    # Initialize the Table object for pypika
    tbl = Table(table_name)

    # Construct the SQL query using pypika
    q = Query.from_(tbl).select("*")
    sql = q.get_sql()

    try:
        # Execute the SQL query and fetch all records
        cursor.execute(sql)
        records = cursor.fetchall()

        # Fetch the column names from the cursor description
        column_names = [desc[0].title() for desc in cursor.description]

        # Use tabulate to print records as a table
        print(tabulate(records, headers=column_names))

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        close_db(conn, cursor)
