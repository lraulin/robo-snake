# A simple class to represent a date with a year, month, and day.
import dateparser


class SimpleDate:
    def __init__(self, date: str):
        parsed = dateparser.parse(date)
        if not parsed:
            raise ValueError(f"Could not parse date: {date}")
        self.year = parsed.year
        self.month = parsed.month
        self.day = parsed.day

    def __str__(self):
        return f"{self.year}-{self.month:02d}-{self.day:02d}"

    def to_us_standard(self):
        return f"{self.month:d}/{self.day:d}/{self.year}"
