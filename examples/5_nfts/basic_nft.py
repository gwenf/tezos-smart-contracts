import smartpy as sp


@sp.module
def main():
    class BasicNFT(sp.Contract):
        def __init__(self, owner, name):
            self.data.owner = owner
            self.data.name = name

        @sp.entrypoint
        def transfer(self, new_owner):
            assert (
                sp.sender == self.data.owner
            ), "Must be the owner of the NFT to initiate a transfer."
            self.data.owner = new_owner


@sp.add_test(name="transfer nft ownership")
def test():
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    eve = sp.test_account("eve").address

    c1 = main.BasicNFT(owner=alice, name="Nice Painting")
    scenario = sp.test_scenario(main)
    scenario += c1

    c1.transfer(bob).run(sender=alice)
    scenario.verify(c1.data.owner == bob)

    c1.transfer(eve).run(sender=alice, valid=False)
