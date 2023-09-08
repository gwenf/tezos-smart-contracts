import smartpy as sp


@sp.module
def main():
    class StoreValue(sp.Contract):
        def __init__(self, val):
            self.data.x = val


@sp.add_test(name="StoreValue Test")
def test():
    scenario = sp.test_scenario(main)
    x_value = 55
    store_value = main.StoreValue(val=x_value)
    scenario += store_value

    scenario.verify(store_value.data.x == x_value)
