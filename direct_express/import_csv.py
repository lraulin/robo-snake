from ctypes import get_last_error
import glob
import os
from direct_express.de_db import (
    de_upsert,
)
from direct_express.dto import DirectExpressTransaction
from common.util import get_text_from_file


def _get_latest_import() -> str:
    list_of_files = glob.glob(r"C:\Users\leera\Downloads\*.csv")
    direct_express_files = [
        filename for filename in list_of_files if "DirectExpress-" in filename
    ]
    try:
        latest_file = max(direct_express_files, key=os.path.getctime)
    except ValueError:
        print("No files found")
        return None
    created_time = os.path.getctime(latest_file)
    return get_text_from_file(latest_file), created_time


def _csv_to_dtos(csv: str, imported_time: int) -> list[DirectExpressTransaction]:
    lines = csv.split("\n")
    header = lines[3]
    if (
        header
        != "DATE,TRANSACTION ID,DESCRIPTION,AMOUNT,TRANSACTION TYPE,CITY,STATE,COUNTRY"
    ):
        raise ValueError("Header is not as expected")
    data = lines[4:]
    dtos = [
        DirectExpressTransaction(line.split(","), imported=imported_time)
        for line in data
        if line != ""
    ]
    return dtos


def _load_csv_data():
    csv, import_time = _get_latest_import()
    dtos = _csv_to_dtos(csv, import_time)
    return dtos


def import_csv():
    print("Importing CSV...")
    dtos = _load_csv_data()
    de_upsert(dtos)
