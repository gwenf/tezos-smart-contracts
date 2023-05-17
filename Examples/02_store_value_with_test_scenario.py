import smartpy as sp
@sp.module
def main():

    class StoreValue(sp.Contract):
        def __init__(self):
            self.data.stored_value = 42

@sp.add_test(name="Testing")
def test():
    scenario = sp.test_scenario(main)
    contract = main.StoreValue()
    scenario += contract
