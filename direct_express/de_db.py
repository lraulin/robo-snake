# Direct Express DB service


from tabulate import tabulate
from common.constants import DB_FILE_NAME
from db.db import close_db, column_max, db_read, db_write, open_db, upsert
from direct_express.dto import DirectExpressTransaction
from pypika import Query, Table, Order
from datetime import datetime

TRANSACTION_ID = "transaction_id"
PENDING = "Pending"
de_transactions = Table("direct_express")
columns = (
    "date",
    "transaction_id",
    "description",
    "amount",
    "transaction_type",
    "city",
    "state",
    "country",
    "imported",
)


def title(l: list[str]) -> list[str]:
    return [s.title() for s in l]


def get_last_transaction_id() -> int:
    id = column_max(de_transactions, "transaction_id")
    print(f"Last transaction id: {id}")
    return id


def get_pending_transaction_ids() -> list[int]:
    q = (
        Query.from_(de_transactions)
        .select(TRANSACTION_ID)
        .where(de_transactions.date == PENDING)
    )
    results = db_read(q)
    print(results)
    return [result[0] for result in results]


def insert_transactions(dtos: list[DirectExpressTransaction]):
    q = Query.into(de_transactions).insert(*[dto.to_sql() for dto in dtos])
    db_write(q)


def de_upsert(dtos: list[DirectExpressTransaction]):
    last_id = get_last_transaction_id()
    records_to_insert = [dto.to_sql() for dto in dtos if dto.transaction_id > last_id]
    print(records_to_insert)

    pending_transaction_ids = get_pending_transaction_ids()
    records_to_update = [
        dto.to_sql() for dto in dtos if dto.transaction_id in pending_transaction_ids
    ]
    print(records_to_update)
    upsert("direct_express", records_to_insert + records_to_update)


def get_transactions(orderby="date"):
    q = Query.from_(de_transactions).select("*").orderby(orderby, order=Order.desc)
    results = db_read(q)
    dtos = [DirectExpressTransaction.from_sql(result) for result in results]
    print(tabulate(dtos, headers="keys", tablefmt="psql"))
    return dtos


def show_transactions(n=0, orderby=["date"]):
    q = Query.from_(de_transactions).select(*columns)

    for column in orderby:
        q = q.orderby(column, order=Order.desc)

    if n != 0:
        q = q.limit(n)

    results = db_read(q)

    # Unix timestamp to datetime
    dt = lambda x: datetime.fromtimestamp(x).isoformat()[:-7]
    i = lambda x: columns.index(x)
    data = [
        [
            *result[: i("amount")],
            abs(result[i("amount")]),
            *result[i("transaction_type") : i("imported")],
            dt(result[i("imported")]),
        ]
        for result in results
    ]

    print(tabulate(data, headers=title(columns), tablefmt="psql", floatfmt=".2f"))
    return
