import re

from simple_date import SimpleDate


def clean_amount(amount_str):
    amount_str = re.sub(r"[,$]", "", amount_str)  # Remove $ and ,
    return float(amount_str)


def clean_date(date_str):
    # Convert MM/DD/YYYY to YYYY-MM-DD
    if date_str == "Pending":
        return "Pending"
    month, day, year = map(int, date_str.split("/"))
    return f"{year:04d}-{month:02d}-{day:02d}"


def clean_text(description):
    return description.encode("ascii", "ignore").decode()  # Remove non-ASCII characters


def clean_record(record):
    (date, transaction_id, description, amount, transaction_type, *rest) = record
    city = rest[0] if len(rest) > 0 else ""
    state = rest[1] if len(rest) > 1 else ""
    country = rest[2] if len(rest) > 2 else ""
    return (
        clean_date(date),
        int(transaction_id),
        clean_text(description),
        clean_amount(amount),
        clean_text(transaction_type),
        clean_text(city),
        clean_text(state),
        clean_text(country),
    )


# A class to parse and store a row of Direct Express transactions.
# It takes a list of strings in its constructor and assigns them to properties.
class DirectExpressTransaction:
    account = "Direct Express"
    institution = "Comerica"
    account_number = "xxxx0947"

    def __init__(self, row):
        row = [cel.encode("ascii", "ignore").decode().strip() for cel in row]

        if row[0] == "Pending":
            self.date = None
            self.is_pending = True
        else:
            self.date = SimpleDate(row[0])
            self.is_pending = False
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
