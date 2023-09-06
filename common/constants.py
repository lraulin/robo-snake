# Description: Constants used throughout the application
DB_FILE_NAME = "db/tiller.db"
DIRECT_EXPRESS_SHEET = "DirectExpress"
DIRECT_EXPRESS_TABLE = "direct_express"
DIRECT_EXPRESS_PENDING = "Pending"
DIRECT_EXPRESS_HEADERS = (
    "DATE,TRANSACTION ID,DESCRIPTION,AMOUNT,TRANSACTION TYPE,CITY,STATE,COUNTRY"
)

data = {
    "transactions": {
        "sheet": {
            "name": "Transactions",
            "Headers": [
                "Date",
                "Description",
                "Category",
                "Amount",
                "Account",
                "Account #",
                "Institution",
                "Month",
                "Week",
                "Transaction ID",
                "Account ID",
                "Check Number",
                "Full Description",
                "Date Added",
                "Categorized Date",
            ],
        },
        "db": {
            "table": "transactions",
        },
    }
}
