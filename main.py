from direct_express.de_db import show_transactions
from direct_express.from_google import update_from_google_sheets


import argparse

from direct_express.import_csv import import_csv
from sheets.api import get_transactions


def not_implemented():
    print("Not implemented")


def parse_args() -> argparse.Namespace:
    # Create the main parser
    parser = argparse.ArgumentParser(description="Financial management database")

    subparsers = parser.add_subparsers(
        dest="command",  # This will contain the name of the subparser command that was used
        help="Sub-command help",
    )

    # Create a Direct Express subparser
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

    # Create a Tiller subparser
    parser_transactions = subparsers.add_parser("trans", help="Tiller Transactions")
    parser_transactions.add_argument(
        "-i", "--import_csv", action="store_true", help="Import from file"
    )
    parser_transactions.add_argument(
        "-g", "--sheets", action="store_true", help="Import from Google Sheets"
    )
    parser_transactions.add_argument(
        "-p",
        "--print",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Show transactions as table, optionally specify a number",
    )
    parser_transactions.set_defaults(func=argparse.SUPPRESS)

    # Create a 'show' subparser for displaying data
    parser_show = subparsers.add_parser(
        "show", aliases=["s"], help="Print a table data"
    )

    # Add a required positional argument
    parser_show.add_argument("table", type=str, help="Required table argument.")

    parser_show.add_argument(
        "number",
        type=int,
        nargs="?",
        default=10,
        help="Optional number of records to display. Default is 10.",
    )

    # Add other optional flags
    parser_show.add_argument("-s", "--sort", help="Sort by column")
    parser_show.add_argument("-f", "--filter", help="Filter by condition")

    args = parser.parse_args()
    return args


def command_is_de(args):
    commands = ["de", "direct_express", "directexpress"]
    command = args.command.lower()
    return command in commands


def direct_express(args) -> None:
    if args.load:
        import_csv()
    elif args.google:
        update_from_google_sheets()


def command_is_show(args) -> bool:
    commands = ["show", "s"]
    command = args.command.lower()
    return command in commands


def show(args) -> None:
    transaction_aliases = ["transactions", "trans", "t"]
    if args.table in transaction_aliases:
        print("Showing transactions")
        not_implemented()

    direct_express_aliases = ["direct_express", "directexpress", "de"]
    if args.table.lower() in direct_express_aliases:
        n = args.number
        print(f"Showing {n} Direct Express transactions")
        show_transactions(n)


def main():
    args = parse_args()
    print(args.command)

    if args.command == "de":
        direct_express(args)
        return

    if args.command == "trans":
        get_transactions()
        return

    if command_is_show(args):
        show(args)
        return


if __name__ == "__main__":
    main()
