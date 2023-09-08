import smartpy as sp


@sp.module
def main():
    class StoreValue(sp.Contract):
        def __init__(self):
            self.data.stored_value = 0

        @sp.entry_point
        def add(self, a):
            assert a <= 10 and a >= 1, "Number must be in range 1 to 10"
            self.data.stored_value += a


@sp.add_test(name="Add")
def test():
    c1 = main.StoreValue()
    scenario = sp.test_scenario(main)
    scenario += c1
    scenario.h3("Testing add entrypoint")
    c1.add(0).run(valid=False, exception="Number must be in range 1 to 10")
    c1.add(9)
    c1.add(1)

    scenario.verify(c1.data.stored_value == 10)
