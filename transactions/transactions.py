class Transaction:
    def __init__(self, **kwargs) -> None:
        self.date = Date(kwargs.get("date"))
        self.description = kwargs.get("description")
        self.amount = kwargs.get("amount")
        self.transaction_type = kwargs.get("transaction_type")
        self.city = kwargs.get("city")
        self.state = kwargs.get("state")
        self.country = kwargs.get("country")
        self.imported = kwargs.get("imported", None)
