import json
import re
from common.constants import DIRECT_EXPRESS_PENDING

from common.simple_date import SimpleDate


def is_pending(row: list[str]) -> bool:
    return row[0] == DIRECT_EXPRESS_PENDING or row[0] == "" or row[0] == None


# A class to parse and store a row of Direct Express transactions.
# It takes a list of strings in its constructor and assigns them to properties.
class DirectExpressTransaction:
    account = "Direct Express"
    institution = "Comerica"
    account_number = "xxxx0947"

    def __init__(self, row: list[str] | str, **kwargs):
        if isinstance(row, str):
            row = row.split(",")
        row: list[str] = [cel.encode("ascii", "ignore").decode().strip() for cel in row]

        self.date = DIRECT_EXPRESS_PENDING if is_pending(row) else SimpleDate(row[0])
        self.is_pending = True if is_pending(row) else False
        self.transaction_id = int(row[1])
        self.description = row[2]
        self.amount = float(re.sub(r"[,$]", "", row[3]))
        self.transaction_type = row[4]
        try:
            self.city = row[5]
        except IndexError:
            self.city = ""
        try:
            self.state = row[6]
        except IndexError:
            self.state = ""
        try:
            self.country = row[7]
        except IndexError:
            self.country = ""

        self.imported = kwargs.get("imported", None)

    def uninit(self):
        return [
            self.date.to_us_standard(),
            self.transaction_id,
            self.description,
            self.amount,
            self.transaction_type,
            self.city,
            self.state,
            self.country,
        ]

    def to_sql(self):
        return (
            str(self.date),
            self.transaction_id,
            self.description,
            self.amount,
            self.transaction_type,
            self.city,
            self.state,
            self.country,
            self.imported,
        )

    def to_dict(self):
        return {
            "date": str(self.date),
            "transaction_id": self.transaction_id,
            "description": self.description,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "imported": self.imported,
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)
