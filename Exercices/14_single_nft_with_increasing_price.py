import smartpy as sp

@sp.module
def main():

    class NftForSale(sp.Contract):
       def __init__(self, owner, metadata, price):
           self.data.owner = owner
           self.data.metadata = metadata
           self.data.price = price
    
       @sp.entrypoint
       def buy(self):
           assert sp.amount == self.data.price
           sp.send(self.data.owner, self.data.price)
           self.data.owner = sp.sender
           self.data.price += sp.split_tokens(self.data.price, 10, 100) 


@sp.add_test(name='Testing Update Price')
def test():
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    eve = sp.test_account("eve").address
    c1 = main.NftForSale(owner = alice, metadata = "Gwen's nft", price=sp.mutez(5000000))
    scenario = sp.test_scenario(main)
    scenario +=c1
    scenario.h3(" Testing increasing price")
    c1.buy().run(sender = bob, amount = sp.mutez(5000000))
    c1.buy().run(sender = eve, amount = sp.mutez(5500000))
    c1.buy().run(sender = alice, amount = sp.mutez(6000000), valid = False)
    scenario.verify(c1.data.price == sp.mutez(6050000))

