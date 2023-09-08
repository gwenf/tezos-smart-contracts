import smartpy as sp


@sp.module
def main():
    class BasicNFT(sp.Contract):
        def __init__(self, owner, name, price):
            self.data.owner = owner
            self.data.name = name
            self.data.price = price

        @sp.entrypoint
        def set_price(self, new_price):
            assert (
                sp.sender == self.data.owner
            ), "Only the owner can change the price"
            self.data.price = new_price

        @sp.entrypoint
        def buy(self):
            assert sp.amount == self.data.price, "Incorrect amount"
            sp.send(self.data.owner, self.data.price)
            self.data.owner = sp.sender


@sp.add_test(name="sell nft")
def test():
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    eve = sp.test_account("eve").address

    c1 = main.BasicNFT(owner=alice, name="Nice Painting", price=sp.tez(2))
    scenario = sp.test_scenario(main)
    scenario += c1

    c1.set_price(sp.tez(4)).run(sender=alice)
    c1.set_price(sp.tez(4)).run(sender=eve, valid=False)

    c1.buy().run(sender=bob, amount=sp.mutez(4_000_000))
    c1.set_price(sp.tez(6)).run(sender=bob)

    c1.buy().run(sender=eve, amount=sp.mutez(4_000_000), valid=False)
