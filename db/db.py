import sqlite3
from common.constants import DB_FILE_NAME


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
