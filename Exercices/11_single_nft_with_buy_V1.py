import smartpy as sp

@sp.module
def main():

    class NftForSale(sp.Contract):
    
       def __init__(self, owner, metadata, price):
           self.data.owner = owner
           self.data.metadata = metadata
           self.data.price = price
    
       @sp.entrypoint
       def set_price(self, new_price):
           assert sp.sender == self.data.owner, "you cannot update the price"
           self.data.price = new_price
    
       @sp.entrypoint
       def buy(self):
           assert sp.amount == self.data.price, "wrong price"
           sp.send(self.data.owner, self.data.price)
           self.data.owner = sp.sender
    
@sp.add_test(name='Testing set_price and buy')
def test():
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    eve = sp.test_account("eve").address
    c1 = main.NftForSale(owner = alice, metadata = "Gwen's first NFT", price = sp.mutez(5000000))
    scenario = sp.test_scenario(main)
    scenario +=c1
    scenario.h3(" Testing set_price entrypoint")
    #testing set price
    c1.set_price(sp.mutez(7000000)).run(sender = alice)
    c1.set_price(sp.tez(5)).run(sender =  bob, valid = False)
    #testing buy entrypoint
    scenario.h3(" Testing buy entrypoint with correct and incorrect prices")
    c1.buy().run(sender=bob, amount=sp.mutez(7000000))
    c1.buy().run(sender=eve, amount=sp.tez(6), valid = False)
