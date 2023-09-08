import smartpy as sp


@sp.module
def main():
    class StoreValue(sp.Contract):
        def __init__(self, min_value, max_value, owner):
            self.data.owner = owner
            self.data.min_value = min_value
            self.data.max_value = max_value
            self.data.original_min = min_value
            self.data.original_max = max_value

        @sp.entrypoint
        def reset(self):
            # assert that the caller of this function is the contract owner
            assert self.data.owner == sp.sender
            self.data.min_value = self.data.original_min
            self.data.max_value = self.data.original_max

        @sp.entrypoint
        def set(self, new_min_value, new_max_value):
            self.data.min_value = new_min_value
            self.data.max_value = new_max_value

        @sp.entrypoint
        def add_number(self, a):
            self.data.min_value += a
            self.data.max_value += a


@sp.add_test(name="testing")
def test():
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address

    c1 = main.StoreValue(min_value=0, max_value=5, owner=alice)
    scenario = sp.test_scenario(main)
    scenario += c1

    scenario.h3(" Setting Min and Max")
    c1.set(new_min_value=5, new_max_value=10)
    scenario.verify(c1.data.min_value == 5)
    scenario.verify(c1.data.max_value == 10)

    c1.reset().run(sender=alice)
    scenario.verify(c1.data.min_value == 0)
    scenario.verify(c1.data.max_value == 5)

    c1.reset().run(sender=bob, valid=False)
    scenario.verify(c1.data.min_value == 0)
    scenario.verify(c1.data.max_value == 5)
