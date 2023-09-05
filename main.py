from direct_express.from_google import update_from_google_sheets


import argparse

from direct_express.import_csv import import_csv


def main():
    parser = argparse.ArgumentParser(description="Financial management database")

    # Create subparsers for each sub-command
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # Define the 'add' sub-command
    parser_direct_express = subparsers.add_parser("de", help="Direct Express")
    parser_direct_express.add_argument(
        "-l", "--load", action="store_true", help="Import from file"
    )
    parser_direct_express.add_argument(
        "-g", "--google", action="store_true", help="Import from Google Sheets"
    )
    parser_direct_express.add_argument(
        "-i",
        "--last-id",
        action="store_true",
        help="Get the most recent transaction id",
    )
    parser_direct_express.set_defaults(func=import_csv)

    # Define the 'subtract' sub-command
    parser_tiller = subparsers.add_parser("tiller", help="Tiller Transactions")
    parser_tiller.add_argument(
        "-i", "--import_csv", action="store_true", help="Import from file"
    )
    parser_tiller.add_argument(
        "-g", action="store_true", help="Import from Google Sheets"
    )
    parser_tiller.set_defaults(func=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.command == "de":
        if args.load:
            import_csv()
        elif args.google:
            update_from_google_sheets()


if __name__ == "__main__":
    main()
