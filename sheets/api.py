from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sheets.auth import get_creds
from sheets.secret import TILLER_SPREADSHEET_ID

TRANSACTIONS_SHEET_NAME = "Transactions"


def get_sheet(sheet_name: str) -> list[list]:
    creds = get_creds()
    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=TILLER_SPREADSHEET_ID, range=sheet_name)
            .execute()
        )
        values = result.get("values", [])[1:]

        if not values:
            print("No data found.")
            return

        return values
    except HttpError as err:
        print(err)


def get_sheet_as_dict(sheet_name: str) -> dict:
    creds = get_creds()
    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=TILLER_SPREADSHEET_ID, range=sheet_name)
            .execute()
        )
        values = result.get("values", [])
        if not values:
            print("No data found.")
            return

        headers = values[0]
        print(headers)
        rows = values[1:]
        return [dict(zip(headers, row)) for row in rows]

    except HttpError as err:
        print(err)


def get_transactions() -> list[list]:
    data = get_sheet_as_dict(TRANSACTIONS_SHEET_NAME)
