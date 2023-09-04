from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sheets.auth import get_creds
from sheets.secret import TILLER_SPREADSHEET_ID


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
