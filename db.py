import sqlite3

from direct_express import clean_record

tables = {
    "DirectExpress": {
        "table": "direct_express",
    },
    "Transactions": {
        "table": "transactions",
    },
}


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


def upsert(db_name, table_name, data):
    cursor, con = get_cursor_and_con(db_name)
    col_names, primary_key = get_table_info(cursor, table_name)

    num_cols = len(col_names)
    place_holders = ("?," * num_cols)[:-1]

    # Excluding the primary key for the update operation
    update_fields = [col for col in col_names if col != primary_key]
    update_clause = ", ".join(
        [f"{field} = excluded.{field}" for field in update_fields]
    )

    clean_data = [clean_record(record) for record in data]
    sql = f"""INSERT INTO {table_name}
              VALUES ({place_holders})
              ON CONFLICT({primary_key})
              DO UPDATE SET {update_clause};"""

    cursor.executemany(sql, clean_data)
    con.commit()
    cursor.close()
    con.close()
    print(f"Successfully upserted {len(data)} records into {table_name}")


# A class for a Direct Express transaction row with the following columns:
# date, transaction_id, description, amount, transaction_type, city, state, country
# It takes them in its constructor in that order and assigns them to properties.
class DirectExpressTransaction:
    def __init__(
        self,
        date,
        transaction_id,
        description,
        amount,
        transaction_type,
        city,
        state,
        country,
    ):
        self.date = date
        self.transaction_id = transaction_id
        self.description = description
        self.amount = amount
        self.transaction_type = transaction_type
        self.city = city
        self.state = state
        self.country = country

    # A method that returns a string representation of the transaction.
    def __str__(self):
        return (
            f"{self.date} {self.transaction_id} {self.description} {self.amount} "
            f"{self.transaction_type} {self.city} {self.state} {self.country}"
        )

    # A method that returns a string representation of the transaction in CSV format.
    def to_csv(self):
        return (
            f"{self.date},{self.transaction_id},{self.description},{self.amount},"
            f"{self.transaction_type},{self.city},{self.state},{self.country}"
        )
