from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from api import get_sheet
from db import upsert

from secret import TILLER_SPREADSHEET_ID


DB_NAME = "tiller.db"


def main():
    direct_express_data = get_sheet("DirectExpress")
    print(direct_express_data)
    upsert(DB_NAME, "direct_express", direct_express_data)


if __name__ == "__main__":
    main()
