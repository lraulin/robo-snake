CREATE TABLE tiller_transactions (
    Date TEXT NOT NULL,
    Description TEXT NOT NULL,
    Category TEXT,
    Amount REAL NOT NULL,
    Account TEXT NOT NULL,
    AccountNumber TEXT,
    Institution TEXT,
    Month TEXT,
    Week TEXT,
    TransactionID TEXT UNIQUE NOT NULL,
    AccountID TEXT,
    CheckNumber TEXT,
    FullDescription TEXT,
    DateAdded TEXT,
    CategorizedDate TEXT,
    PRIMARY KEY(TransactionID)
);