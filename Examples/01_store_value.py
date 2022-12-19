import smartpy as sp

class StoreValue(sp.Contract):
    def __init__(self):
        self.init(
            storedValue = 42
        )
