from common.constants import DIRECT_EXPRESS_SHEET
from db.db import upsert
from direct_express.dto import DirectExpressTransaction
from sheets.api import get_sheet


def update_from_google_sheets() -> list[DirectExpressTransaction]:
    """Gets data from the Google Sheet."""
    sheet = get_sheet(DIRECT_EXPRESS_SHEET)
    tuples = [DirectExpressTransaction(row).to_sql() for row in sheet]
    print(tuples)
    upsert("direct_express", tuples)
