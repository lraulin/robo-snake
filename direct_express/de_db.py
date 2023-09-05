# Direct Express DB service


from common.constants import DB_FILE_NAME
from db.db import close_db, column_max, db_read, db_write, open_db, upsert
from direct_express.dto import DirectExpressTransaction
from pypika import Query, Table

TRANSACTION_ID = "transaction_id"
PENDING = "Pending"
de_transactions = Table("direct_express")


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
