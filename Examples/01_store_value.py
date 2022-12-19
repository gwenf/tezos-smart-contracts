import smartpy as sp

class StoreValue(sp.Contract):
    def __init__(self):
        self.init(
            storedValue = 42
        )

@sp.add_test(name="Testing")
def test():
    scenario = sp.test_scenario()
    contract = StoreValue()
    scenario += contract
    