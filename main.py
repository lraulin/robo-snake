from db.db import insert_categories
from direct_express.from_file import get_latest_import, update_from_file
from direct_express.from_google import update_from_google_sheets


def main():
    insert_categories()


if __name__ == "__main__":
    main()
